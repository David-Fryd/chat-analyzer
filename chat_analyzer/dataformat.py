import json
import numpy as np
import logging

from argparse import ArgumentTypeError
from dataclasses import dataclass,field
from abc import ABC, abstractclassmethod
from .chat_downloader.sites.common import Chat
from typing import List

from .chat_downloader.utils.core import seconds_to_time

# The platforms we currently support downloading from.
# Each has a corresponding ChatAnalytics/Sample extension with site-specific behavior
YOUTUBE_NETLOC = 'www.youtube.com'
YOUTUBE_SHORT_NETLOC = 'youtu.be'
TWITCH_NETLOC = 'www.twitch.tv'
SUPPORTED_PLATFORMS = [YOUTUBE_NETLOC, TWITCH_NETLOC, YOUTUBE_SHORT_NETLOC]
SUPPORTED_PLATFORMS_SHORTHANDS = {
    # Useful for CLI choices when specifying the source of the chatfile
    "youtube" : YOUTUBE_NETLOC,
    "twitch" : TWITCH_NETLOC
}


# The formatting to print the progress status with
PROG_PRINT_TEMPLATE = "{:^15}| {:^25} | {:^20}"

METRIC_TO_FIELD = {
    # Used to convert the engagement-metric provided by the CLI to the actual field name of the sample class
    "activityPSec": "avgActivityPerSecond",
    "chatsPSec" : "avgChatMessagesPerSecond",
    "usersPSec" : "avgUniqueUsersPerSecond",
}

@dataclass
class ProcessSettings():
    """
    Utility class for passing information from the analyzer to the chatlog processor and post-processor
    
    print_interval: int 
        After ever 'progress_interval' messages, print a progress message. If <=0, progress printing is disabled
    msg_break: int
        (Mainly for Debug) Stop processing messages after BREAK number of messages have been processed. 
    highlight_percentile: float 
        The cutoff percentile that samples must meet to be considered a highlight
    highlight_metric: str
        The metric to use for engagement analysis to build highlights. NOTE: must be converted into actual Sample field name before use.
    spike_sensitivity: float 
        How sensitive the spike detector is at picking up spikes. Higher sensitivity means more spikes are detected.

    """
    # Processing (Sampling) Arguments
    print_interval: int
    msg_break: int
    # Post-processing (Analyzing) Arguments
    highlight_percentile: float
    highlight_metric: str
    spike_sensitivity: float


# NOTE: Yes CamelCased fields in the dataclasses are unpythonic, but the primary intention is to convert these dataclasses into JSON objects and it is one less step to handle then!
@dataclass
class Sample():
    """
    Class that contains data of a specific time interval of the chat.
    Messages will be included in a sample if they are contained within [startTime, endTime)

    ---

    **[Defined when class Initialized]**:

    startTime: float
        The start time (inclusive) (in seconds) corresponding to a sample.
    endTime: float
        The end time (exclusive) (in seconds) corresponding to a sample.
    

    **[Automatically Defined on init]**:

    startTime_text: str
        The start time represented in text format (i.e. hh:mm:ss)
    endTime_text: str
        The end time represented in text format (i.e. hh:mm:ss)
    sampleDuration: float
        The duration (in seconds) of the sample (end-start)
        NOTE: Should be == to the selected interval in all except the last sample if the total duration of the chat is not divisible by the interval


    **[Defined w/ default and modified DURING analysis of sample]**:

    activity: int
        The total number of messages/things (of any type!) that appeared in chat within the start/endTime of this sample.
        Includes messages,notifications,subscriptions, superchats, . . . *anything* that appeared in chat
    chatMessages: int
        The total number of chats sent by human (non-system) users (what is traditionally thought of as a chat)
        NOTE: Difficult to discern bots from humans other than just creating a known list of popular bots and blacklisting, 
        because not all sites (YT/Twitch) provide information on whether chat was sent by a registered bot or not.
    firstTimeChatters: int
        The total number of users who sent their first message of the whole stream during this sample interval


    **[Defined w/ default and modified AFTER analysis of sample]**:
    
    uniqueUsers: int
        The total number of unique users that sent a chat message (len(self._userChats))
    avgActivityPerSecond: float
        The average activity per second across this sample interval. (activity/sampleDuration)
    avgChatMessagesPerSecond: float
        The average number of chat messages per second across this sample interval. (totalChatMessages/sampleDuration)
    avgUniqueUsersPerSecond: float
        The average number of unique users that sent a chad across this sample interval. (uniqueUsers/sampleDuration)

    """

    # Defined when class Initialized
    startTime: float
    endTime: float

    # Automatically re-defined on post-init
    sampleDuration: float = -1
    startTime_text: str = ''
    endTime_text: str = ''

    # Defined w/ default and modified DURING analysis of sample
    activity: int = 0 
    chatMessages: int = 0
    firstTimeChatters: int = 0

    # Defined w/ default and modified AFTER analysis of sample
    uniqueUsers: int = 0
    avgActivityPerSecond: float = 0
    avgChatMessagesPerSecond: float = 0
    avgUniqueUsersPerSecond: float = 0

    # Internal Fields used for calculation but are #NOTE: NOT EXPORTED during json dump (deleted @ post_process)
    _userChats: dict = field(default_factory=dict) # author['id'] -> numChats for current sample

    def __post_init__(self):
            self.startTime_text = seconds_to_time(self.startTime)
            self.endTime_text = seconds_to_time(self.endTime)
            self.sampleDuration = self.endTime - self.startTime

    def sample_post_process(self):
        """
        After we have finished adding messages to a particular sample (moving on to the next sample),
        we call sample_post_process() to process the cumulative data points (so we don't have to do this every time we add a message)

        Also removes the internal fields that don't need to be output in the JSON object.

        """
        self.uniqueUsers = len(self._userChats)

        if self.sampleDuration > 0:
            self.avgActivityPerSecond = self.activity/self.sampleDuration
            self.avgChatMessagesPerSecond = self.chatMessages/self.sampleDuration
            self.avgUniqueUsersPerSecond = self.uniqueUsers/self.sampleDuration
        else:
            logging.warning(f"Sample was created with duration < 0 (duration: {self.sampleDuration}): {self}")

        self._userChats.clear()
@dataclass
class TwitchSample(Sample):
    """
    Class that contains data specific to Twitch of a specific time interval of the chat.
    
    ---

    **[Defined w/ default and modified DURING analysis of sample]**:

    subscriptions: int
        The total number of subscriptions (that people purhcased themselves) that appeared in chat within the start/endTime of this sample.
    giftSubscriptions: int
        The total number of gift subscriptions that appeared in chat within the start/endTime of this sample.
    upgradeSubscriptions: int
        The total number of upgraded subscriptions that appeared in chat within the start/endTime of this sample.
    """
    #Defined w/ default and modified DURING analysis of sample
    subscriptions: int = 0
    giftSubscriptions: int = 0
    upgradeSubscriptions: int = 0
@dataclass
class YoutubeSample(Sample):
    """
    Class that contains data specific to Youtube of a specific time interval of the chat.
    
    ---

    **[Defined w/ default and modified DURING analysis of sample]**:

    superchats: int
        The total number of superchats (regular/ticker) that appeared in chat within the start/endTime of this sample.
        NOTE: A creator doesn't necessarily care what form a superchat takes, so we just combine regular and ticker superchats
    memberships: int
        The total number of memberships that appeared in chat within the start/endTime of this sample.
    """
    # Defined w/ default and modified DURING analysis of sample
    superchats: int = 0
    memberships: int = 0
    

@dataclass
class Section():
    """
    Contains generic information about a noteable section of the chatlog
    
    ---

    **[Defined when class Initialized]**:

    startTime: float
        The start time (inclusive) (in seconds) corresponding to a section.
    endTime: float
        The end time (exclusive) (in seconds) corresponding to a section.
    description: str (optional)
        A description of the section (if any).

    **[Automatically re-defined on post-init]**:

    duration: float
        The duration (in seconds) of the section (end-start)
    duration_text: str
        The duration represented in text format (i.e. hh:mm:ss)
    startTime_text: str
        The start time represented in text format (i.e. hh:mm:ss)
    endTime_text: str
        The end time represented in text format (i.e. hh:mm:ss)

    """
    # Defined when class Initialized
    startTime: float
    endTime: float
    description: str 

    # Automatically defined on init (still have to set defaults b/c of @dataclass sublcass)
    duration: float = field(default=0.0, init=False)
    duration_text: str = field(default='', init=False)
    startTime_text: str = field(default='', init=False)
    endTime_text: str = field(default='', init=False)

    def __post_init__(self):
        self.duration = self.endTime - self.startTime
        self.duration_text = seconds_to_time(self.duration)
        self.startTime_text = seconds_to_time(self.startTime)
        self.endTime_text = seconds_to_time(self.endTime)
@dataclass
class Highlight(Section):
    """
    Highlights reference a contiguous period of time where the provided metric remains above the percentile threshold.
    
    ---

    type: str
        The engagement metric. i.e. "avgActivityPerSecond", "avgChatMessagesPerSecond", "avgUniqueUsersPerSecond", etc.
        NOTE: It is stored as its converted value (the name of the actual field), NOT the metric str the user provided in the CLI.
    peak: float
        The maximum value of the engagement metric throughout the whole Highlight (among the samples in the Highlight). 
    avg: float
        The average value of the engagement metric throughout the whole Highlight (among the samples in the Highlight).
    
    """
    type: str
    peak: float
    avg: float

class Spike(Section):
    """
    Contains information about an activity spike in the chatlog
    
    TODO: Implement

    ---
    ...
    """
    # TODO: Implement


@dataclass
class ChatAnalytics(ABC):
    """
    Class that contains the results of the chat data analysis/processing.
    
    An instance of a subclass is created and then modified throughout 
    the analysis process. After the processing of the data is complete,
    the object will contain all relevant results we are looking for.

    This class cannot be directly instantiated, see the subclasses
    YoutubeChatAnalytics & TwitchChatAnalytics. YT and Twitch
    chats report/record data differently and contain site-specific
    events, so we centralize common data/fxnality and separate
    specifics into subclasses.

    The object can then be converted to JSON/printed/manipulated as
    desired to format/output the results as necessary.

    ---

    **[Defined when class Initialized]**:

    duration: float
        The total duration (in seconds) of the associated video/media. Message times correspond to the video times.
    interval: int
        The time interval (in seconds) at which to compress datapoints into samples. i.e. Duration of the samples. The smaller the interval, the more 
        granular the analytics are. At interval=5, each sample contains 5 seconds of cumulative data.
        *(With the exception of the last sample, which may be shorter than the interval.)* 
        This is b/c media duration is not necessarily divisible by the interval.
        #(samples in raw_data) is about (video duration/interval) (+1 if necessary to encompass remaining non-divisible data at end of data).
    description: str
        A description included to help distinguish it from other analytical data.
    program_version: str
        The version of the chat analytics program that was used to generate the data. Helps identify outdated/version-specific data formats.
    platform: str
        Used to store the platform the data came from: 'www.youtube.com', 'www.twitch.tv', 'youtu.be'...
        While it technically can be determined by the type of subclass, this makes for easier conversion to JSON/output


    **[Automatically re-defined on post-init]**:

    duration_text: str
        String representation of the media duration time.
    interval_text: str
        String representation of the interval time.

    **[Defined w/ default and modified DURING analysis]**:

    mediaTitle: str
        The title of the media associated with the chatlog.
    mediaSource: str
        The link to the media associated with the chatlog (url that it was origianlly downloaded from or filepath of a chatfile).
    samples: List[Sample]
        An array of sequential samples, each corresponding to data about a section of chat of 'interval' seconds long.
        Each sample has specific data corresponding to a time interval of the vid. See the 'Sample' class
    totalActivity: int
        The total number of messages/things (of any type!) that appeared in chat. (Sum of intervalActivity from all samples) 
        Includes messages,notifications,subscriptions, superchats, . . . *anything* that appeared in chat
    totalChatMessages: int
        The total number of chats sent by human (non-system) users (what is traditionally thought of as a chat)
        NOTE: Difficult to discern bots from humans other than just creating a known list of popular bots and blacklisting, 
        because not all sites (YT/Twitch) provide information on whether chat was sent by a registered bot or not.


    **[Defined w/ default and modified AFTER analysis]**:
    
    totalUniqueUsers: int
        The total number of unique users that sent a chat message (human users that sent at least one traditional chat)
    overallAvgActivityPerSecond: float
        The average activity per second across the whole chatlog. (totalActivity/totalDuration)
    overallAvgChatMessagesPerSecond: float
        The average number of chat messages per second across the whole chatlog. (totalChatMessages/totalDuration)
    overallAvgUniqueUsersPerSecond: float
        The average number of unique users chatting per second.
    highlights: List[Highlight] 
        A list of the high engagement sections of the chatlog.
    highlights_duration: float
        The cumulative duration of the highlights (in seconds)
    highlights_duration_text: str
        The cumulative duration of the highlights represented in text format (i.e. hh:mm:ss)
    spikes: List[Spike]
        Not yet implemented TODO
        A list of the calculated spikes in the chatlog. May contain spikes of different types, identifiable by the spike's type field.
    """
    # Defined when class Initialized
    duration: float
    interval: int
    description: str
    program_version: str
    platform: str

    # Automatically re-defined on post-init
    duration_text: str = ''
    interval_text: str = ''

    # Defined w/ default and modified DURING analysis
    mediaTitle: str = 'No Media Title'
    mediaSource: str = 'No Media Source'

    samples: List[Sample] = field(default_factory=list)

    totalActivity: int = 0
    totalChatMessages: int = 0
    totalUniqueUsers: int = 0

    # Defined w/ default and modified AFTER analysis (post processing)
    overallAvgActivityPerSecond: float = 0
    overallAvgChatMessagesPerSecond: float = 0
    overallAvgUniqueUsersPerSecond: float = 0
    highlights: List[Highlight] = field(default_factory=list)
    highlights_duration: float = 0 
    highlights_duration_text: str = ''
    spikes: List[Spike] = field(default_factory=list) # TODO: Not implemented yet

    # Internal Fields used for calculation but are #NOTE: NOT EXPORTED during json dump (deleted @ post_process)
    _overallUserChats: dict = field(default_factory=dict) # author['id'] -> numChats for full duration
    _currentSample: Sample = None # field(default_factory=None)

    # Constants (not dumped in json)
    _txt_msg_types = {'text_message'} # Messages we just consider regular text_message

    def __post_init__(self):
        self.duration_text = seconds_to_time(self.duration)
        self.interval_text = seconds_to_time(self.interval)
    
    def create_new_sample(self):
        """
        Post-processes the previous sample, then appends & creates a new sample
        following the previous sample sequentially. If a previous sample doesn't exist, 
        creates the first sample.

        NOTE: If there there are only 2 chats, one at time 0:03, and the other at 5:09:12,
        there are still a lot of empty samples in between (because we still want to graph/track the silence times with temporal stability)
        """

        # We need a new sample, process the last one and create a new sample
        new_sample_start_time = 0 # NOTE: Some chatlogs have chats that start at negative time samples. (Presumably chats right before the video starts). We ignore these for now
        if(self._currentSample != None):
            # process the last sample before creating new one (should have already been appended on creation)
            self._currentSample.sample_post_process()
            new_sample_start_time = self._currentSample.endTime
        
        # New sample end time will not extend past the length of the video
        new_sample_end_time = min(new_sample_start_time + self.interval, self.duration)

        if(self.platform==YOUTUBE_NETLOC or self.platform==YOUTUBE_SHORT_NETLOC):
            self._currentSample = YoutubeSample(startTime=new_sample_start_time, endTime=new_sample_end_time)
        elif(self.platform==TWITCH_NETLOC):
            self._currentSample = TwitchSample(startTime=new_sample_start_time, endTime=new_sample_end_time)
        else:
            # If we have arrived here, we assume we support the platform but it has no sample-specific concerns
            self._currentSample = Sample(startTime=new_sample_start_time, endTime=new_sample_end_time)

        self.samples.append(self._currentSample)

    def process_message(self, msg):
        """Given a msg object from chat, update appropriate statistics based on the chat"""

        msg_time_in_seconds = msg['time_in_seconds']

        if(msg_time_in_seconds < 0 or msg_time_in_seconds > self.duration):
            return # If the message comes before or after the duration of associated media, ignore the msg and don't process it

        # Before processing the msg, make sure that msg belongs with the current sample
        if(self._currentSample == None or msg_time_in_seconds >= self._currentSample.endTime):
            self.create_new_sample()

        # Every type of message contributes to total activity
        self.totalActivity += 1
        self._currentSample.activity += 1

        if(msg['message_type'] in self._txt_msg_types): # text_message is a traditional chat
            self.totalChatMessages += 1
            self._currentSample.chatMessages += 1

            if 'author' in msg:
                author = msg['author']
                authID = author['id']
                if authID in self._overallUserChats:
                    self._overallUserChats[authID] = self._overallUserChats[authID] + 1
                else:
                    self._overallUserChats[authID] = 1
                    self._currentSample.firstTimeChatters += 1

                # keeps track of unique user per *sample*
                self._currentSample._userChats[authID] = self._currentSample._userChats[authID] + 1 if authID in self._currentSample._userChats else 1

    # def get_engagement_sections(self):
    #     # Use a two pointer approach to find the start and end of each engagement section
    #     # (1 min, 5 min, 10 min, highest engagement, or smth like that)
    #     raise NotImplementedError
    def get_spikes(self, spike_sensitivity, spike_metric):
        """
        A spike is a point in the chatlog where from one sample to the next, there is a sharp increase in the provided metric.

        ...? Are spikes sustained or..?
        ?:
        A spike is a point in the chatlog where the activity is significantly different from the average activity.
        Activity is significantly different if it is > avg*SPIKE_MULT_THRESHOLD.
        We detect a spike if the high activity level is maintained for at least SPIKE_SUSTAIN_REQUIREMENT # of samples.
        """    
        raise NotImplementedError

    def get_highlights(self, highlight_metric: str, highlight_percentile: float):
        """
        Highlights reference a contiguous period of time where the provided metric remains above the percentile threshold.
        Find and return a list of highlights referencing the start and end times of samples whose highlight_metric is in
        the highlight_percentile for contiguous period of time of the referenced samples.

        A highlight may reference more than one sample if contiguous samples meet the percentile cutoff.

        Samples in the top 'percentile'% of the selected engagement metric will be considered high-engagement samples and included in the highlights output list. 
        The larger the percentile, the greater the metric requirement before being reported. If 'engagement-percentile'=93.0, any sample in the 93rd percentile (top 7.0%%) of the selected metric will be considered an engagement highlight.

        These high-engagement portions of the chatlog are stored as highlights, and may last for multiple samples.

        This method should only be called after the averages have been calculated,
        ensuring accurate results when determining periods of high engagement.

        :param highlight_metric: The metric samples are compared to determine if they are high-engagement samples. NOTE: Internally converted to the actual field name of a sample field.
        :type field_to_use: str
        :param highlight_percentile: The cutoff percentile that the samples must meet to be included in a highlight
        :type percentile: float
        :return: a list of highlights referencing samples that met the percentile cutoff requirements for the provided metric
        :rtype: List[Highlight]
        """        

        highlights: List[Highlight] = []

        field_to_use = METRIC_TO_FIELD[highlight_metric]

        # In order to calculate the percentile cutoff, we have to do two passes. 
        # First to calculate the cutoff, second to find the samples that meet the cutoff.
        field_values = [getattr(s, field_to_use) for s in self.samples]
        percentile_value_cutoff = np.percentile(field_values, [highlight_percentile])

        _firstSample: Sample = None
        _lastSample: Sample = None
        _peak: float = 0
        _avg: float = 0
        _num_samples_in_highlight: int = 0

        for sample in self.samples:
            if(getattr(sample, field_to_use) >= percentile_value_cutoff):
                _num_samples_in_highlight += 1
                # If first sample is not null set first sample to current sample
                if(_firstSample == None):
                    _firstSample = sample
                # TODO: Bugcheck _peak on summit's 14hr and ensure there is exactly 1 highlight w peak of 11 (highlight startTime: 31590, endTime: 31700)
                _peak = max(_peak, getattr(sample, field_to_use)) # peak = max of the current peak and the current sample's activity
                _avg += getattr(sample, field_to_use) # average calculated right before highlight constructed
                # Set the last sample to the current sample
                _lastSample = sample
            else:
                # We are either finished with a highlight, or we are not in a highlight
                # If we were building a highlight, append the highlight to the highlight list and reset internal variables
                if(_firstSample != None):
                    if(_avg!=0):
                        _avg /= _num_samples_in_highlight
                    highlight = Highlight(
                        startTime=_firstSample.startTime,
                        endTime=_lastSample.endTime, 
                        peak=_peak, 
                        avg=_avg, 
                        type=field_to_use, 
                        description=f"{field_to_use} sustained at or above {percentile_value_cutoff}")
                    highlights.append(highlight)
                    self.highlights_duration += highlight.duration
                    # Reset calculation vals for the next highlight
                    _firstSample = None
                    _lastSample = None
                    _peak = 0
                    _avg = 0
                    _num_samples_in_highlight = 0

        return highlights

    def chatlog_post_process(self, settings: ProcessSettings):
        """
        After we have finished iterating through the chatlog and constructing all of the samples,
        we call chatlog_post_process() to process the cumulative data points (so we don't have to do this every time we add a sample).

        This step is sometimes referred to as "analysis".

        Also removes the internal fields that don't need to be output in the JSON object.

        :param settings: Utility class for passing information from the analyzer to the chatlog processor and post-processor
        :type settings: ProcessSettings
        """
        print(f"\nDownloaded & Processed {self.totalActivity} messages.")
        print("Post-processing (Analyzing)...")

        self.totalUniqueUsers = len(self._overallUserChats)

        # NOTE: We calculate actualDuration because if the analyzer is stopped before processing all samples, the duration of the samples does not correspond to the media length
        # This is an unusual case, generally only important when testing, but also keeps in mind future extensibility
        actualDuration = (len(self.samples)-1)*self.interval
        actualDuration += self.samples[-1].sampleDuration

        self.overallAvgActivityPerSecond = self.totalActivity/actualDuration
        self.overallAvgChatMessagesPerSecond = self.totalChatMessages/actualDuration
        # Need to calculate unique users per second based on sample unique users, totalUniqueUsers/duration doesn't tell us what we want to know
        self.overallAvgUniqueUsersPerSecond =  sum(s.avgUniqueUsersPerSecond for s in self.samples)/len(self.samples) 

        # Process and remove the final sample from the currentSample field
        if(self._currentSample): # Won't exist if we read in the obj from a file with it missing already
            self._currentSample.sample_post_process()

        # Highlights & Spikes are determined after the final averages have been calculated
        self.highlights = self.get_highlights(settings.highlight_metric, settings.highlight_percentile)
        self.highlights_duration_text = seconds_to_time(self.highlights_duration)
        # self.spikes = self.get_spikes('avgUniqueUsersPerSecond', settings.spike_percentile) #TODO: Implement spikes

        # Remove all other internal variables not suitable for output
        # del self._overallUserChats
        self._overallUserChats.clear()
        # del self._currentSample
        self._currentSample = None

        print("Post-processing (Analyzing) complete!")

    def process_chatlog(self, chatlog: Chat, source: str, settings: ProcessSettings):
        """
        Iterates through the whole chatlog and calculates the analytical data (Modifies and stores in a ChatAnalytics object). 

        :param chatlog: The chatlog we have downloaded 
        :type chatlog: chat_downloader.sites.common.Chat
        :param source: The source of the media associated w the chatlog. URL of the media we have downloaded the log from, or a filepath
        :type source: str
        :param settings: Utility class for passing information from the analyzer to the chatlog processor and post-processor
        :type settings: ProcessSettings
        """

        # Display progress as chats are downloaded/processed
        print("Processing (Sampling) chat data...")

        # Header
        if(settings.print_interval > 0):
            print("\033[1m"+PROG_PRINT_TEMPLATE.format("Completion", "Processed Media Time", "# Messages Processed")+"\033[0m")

        self.mediaTitle = chatlog.title
        self.mediaSource = source
        
        # For each message of all types in the chatlog:
        for idx, msg in enumerate(chatlog):
            # Display progress every UPDATE_PROGRESS_INTERVAL messages
            if(settings.print_interval > 0 and idx%settings.print_interval==0 and idx!=0):
                self.print_process_progress(msg, idx)   
            # TODO: Remove (DEBUG)
            if idx==settings.msg_break:
                break

            self.process_message(msg)

        if(settings.print_interval > 0):
            self.print_process_progress(None, None, finished=True)

        # Calculate the [Defined w/ default and modified after analysis] fields of the ChatAnalytics
        self.chatlog_post_process(settings)

    def print_process_progress(self, msg, idx, finished=False):
        """
        Prints progress of the chat download/process to the console.

        If finished is true, normal printing is skipped and the last bar of progress is printed.
        This is important because we print progress every UPDATE_PROGRESS_INTERVAL messages, and the total number of 
        messages is not usually divisible by this. We therefore have to slightly change the approach to printing progress for this special case.
        """

        if(finished):
            print(PROG_PRINT_TEMPLATE.format("(100%)", f"{seconds_to_time(self.duration)} / {seconds_to_time(self.duration)}", f"{self.totalActivity}", f"Processed {self.totalActivity} messages"), end='\r')
        else:
            # Progress stats
            completion: float = round((float(msg['time_in_seconds'])/self.duration)*100, 2) # Completion %
            processed_media_time: str = msg['time_text']
            total_duration: str = seconds_to_time(self.duration)
            msgs_processed: int = idx
            print(PROG_PRINT_TEMPLATE.format(f"({completion}%)", f"{processed_media_time} / {total_duration}", f"{self.totalActivity}", f"Processed {msgs_processed} messages"), end='\r')

    def to_JSON(self):
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
@dataclass
class YoutubeChatAnalytics(ChatAnalytics):
    """
    Extension of the ChatAnalytics class, meant to contain data that all chats have
    and data specific to YouTube chats.

    NOTE: Most youtube-specific attributes don't make a lot of sense to continously report a per-second value,
    so we don't!

    ---


    (See ChatAnalytics class for common fields and descriptions)

    **[Defined w/ default and modified DURING analysis]**:

    totalSuperchats: int
        The total number of superchats (regular/ticker) that appeared in the chat.
        NOTE: A creator doesn't necessarily care what form a superchat takes, so we just combine regular and ticker superchats
    totalMemberships: int
        The total number of memberships that appeared in the chat.
    
    """

    # Defined w/ default and modified DURING analysis
    totalSuperchats: int = 0
    totalMemberships: int = 0

    # Constants (not dumped in json)
    _superchat_msg_types = {'paid_message', 'paid_sticker', 'ticker_paid_message_item', 'ticker_paid_sticker_item', 'ticker_sponsor_item'}

    def __post_init__(self):
        super().__post_init__()
        # Adds typing to the current sample (safer dev to ensure fields contained within specific sample type)
        self._currentSample: YoutubeSample = self._currentSample

    def process_message(self, msg):
        """Given a msg object from chat, update common fields and youtube-specific fields"""
        super().process_message(msg)
               
        if(msg['message_type'] in self._superchat_msg_types):
            self.totalSuperchats += 1
            self._currentSample.superchats += 1
        if(msg['message_type'] == 'membership_item'):
            self.totalMemberships += 1
            self._currentSample.memberships += 1
    
    #  # TODO: Remove Print statements [DEBUG]
    #     if(msg['message_type']!='text_message' and msg['message_type'] not in self._superchat_msg_types and msg['message_type']!='membership_item'):
    #         print("\033[1;31mType:" + msg['message_type'] + "\033[0m")
    #         # print("\033[1;33mGroup:" + msg['message_group'] + "\033[0m")
    #         print(msg)

    def to_JSON(self):
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
@dataclass
class TwitchChatAnalytics(ChatAnalytics):
    """
    Extension of the ChatAnalytics class, meant to contain data that all chats have
    and data specific to Twitch chats.

    NOTE: Most twitch-specific attributes don't make a lot of sense to continously report a per-second value,
    so we don't!

    ---

    (See ChatAnalytics class for common fields)

    **[Defined w/ default and modified DURING analysis]**:
    
    totalSubscriptions: int
        The total number of subscriptions that appeared in the chat (which people purchased themselves).
    totalGiftSubscriptions: int
        The total number of gift subscriptions that appeared in the chat.
    totalUpgradeSubscriptions: int
        The total number of upgraded subscriptions that appeared in the chat.

    """
    
    # Defined w/ default and modified DURING analysis
    totalSubscriptions: int = 0
    totalGiftSubscriptions: int = 0
    totalUpgradeSubscriptions: int = 0


    # Constants (not dumped in json)
    _subscription_msg_types = {'subscription', 'resubscription', 'extend_subscription', 'standard_pay_forward', 'community_pay_forward'}
    _gift_sub_msg_types = {'subscription_gift' , 'anonymous_subscription_gift' , 'anonymous_mystery_subscription_gift', 'mystery_subscription_gift', 'prime_community_gift_received'}
    _upgrade_sub_msg_types = {'prime_paid_upgrade', 'gift_paid_upgrade', 'reward_gift', 'anonymous_gift_paid_upgrade'}

    def __post_init__(self):
        super().__post_init__()
        # Add this to text message types so that txt messages are processed in super process along with other txt messages
        self._txt_msg_types.add('highlighted_message')
        self._txt_msg_types.add('send_message_in_subscriber_only_mode')
        # Adds typing to the current sample (safer dev to ensure fields contained within specific sample type)
        self._currentSample: TwitchSample = self._currentSample

    def chatlog_post_process(self, settings):
        super().chatlog_post_process(settings)

    def process_message(self, msg):
        """Given a msg object from chat, update common fields and twitch-specific fields"""
        super().process_message(msg)
        if(msg['message_type'] in self._subscription_msg_types):
            self.totalSubscriptions += 1
            self._currentSample.subscriptions += 1
        
        if(msg['message_type'] in self._gift_sub_msg_types):
            self.totalGiftSubscriptions += 1
            self._currentSample.giftSubscriptions += 1
        
        if(msg['message_type'] in self._upgrade_sub_msg_types):
            self.totalUpgradeSubscriptions += 1
            self._currentSample.upgradeSubscriptions += 1

    # # TODO: Remove Print statements [DEBUG]
    # if(msg['message_type'] not in self._txt_msg_types and msg['message_type'] not in self._subscription_msg_types and msg['message_type'] not in self._upgrade_sub_msg_types and msg['message_type'] not in self._gift_sub_msg_types):
    #     print("\033[1;31mType:" + msg['message_type'] + "\033[0m")
    #     # print(msg)
    
    def to_JSON(self):
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
