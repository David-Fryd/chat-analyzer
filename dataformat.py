import json
from argparse import ArgumentTypeError
from dataclasses import dataclass,field
from abc import ABC, abstractclassmethod
from chat_downloader.sites.common import Chat
from typing import List
import logging

from chat_downloader.utils.core import seconds_to_time

# The platforms we currently support downloading from.
# Each has a corresponding ChatAnalytics extension with site-specific behavior
YOUTUBE_NETLOC = 'www.youtube.com'
TWITCH_NETLOC = 'www.twitch.tv'
SUPPORTED_PLATFORMS = [YOUTUBE_NETLOC, TWITCH_NETLOC]

# How many times larger a data point must be from its average to be considered a "spike"
# Lower sensitivities mean more data points are considered "spikes", resulting in more false positives
# SHOULD BE > 1, Values <=1 result in undesireable behavior (stuff that is below average is considered a spike)
SPIKE_SENSITIVITY: float = 2.0
# TODO: Control SPIKE_SENSITIVITY with options argparse

# How many samples must the activity exceed avg*SPIKE_SENSITIVITY to be considered a "spike"
# The smaller the sample size, the larger this number should probably be.
SPIKE_SUSTAIN_REQUIREMENT: int = 2
# TODO: Control SPIKE_SUSTAIN_REQUIREMENT with options argparse

# NOTE: Yes CamelCased fields in the dataclasses are unpythonic, but the primary intention is to convert these dataclasses into JSON objects and it is one less step to handle then!

@dataclass
class Sample():
    # TODO: Implement subclasses
    # TODO: Implement max-per-sample in addition to average for other fields
    """
    Class that contains data of a specific time interval of the chat.
    Messages will be included in a sample if they are contained within [startTime, endTime)
    
    ---

    Attributes:
        [Defined when class Initialized]
        startTime: float
            The start time (inclusive) (in seconds) corresponding to a sample.
        endTime: float
            The end time (exclusive) (in seconds) corresponding to a sample.
        
        [Automatically Defined on init]
        startTime_text: str
            The start time represented in text format (i.e. hh:mm:ss)
        endTime_text: str
            The end time represented in text format (i.e. hh:mm:ss)
        sampleDuration: float
            The duration (in seconds) of the sample (end-start)
            NOTE: Should be == to the selected interval in all except the last sample if the total duration of the chat is not divisible by the interval

        [Defined w/ default and modified DURING analysis of sample]
        activity: int
            The total number of messages/things (of any type!) that appeared in chat within the start/endTime of this sample.
            Includes messages,notifications,subscriptions, superchats, . . . *anything* that appeared in chat
        chatMessages: int
            The total number of chats sent by human (non-system) users (what is traditionally thought of as a chat)
            NOTE: Difficult to discern bots from humans other than just creating a known list of popular bots and blacklisting, 
            because not all sites (YT/Twitch) provide information on whether chat was sent by a registered bot or not.
        firstTimeChatters: int
            The total number of users who sent their first message of the whole stream during this sample interval

        [Defined w/ default and modified AFTER analysis of sample]
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
            # TODO: Look at the chat-analyzer log function and use that instead for consistency?
            logging.warning(f"Sample was created with duration < 0 (duration: {self.sampleDuration}): {self}")

        # TODO: Remove this temporary measure
        # del self._userChats # TODO: Fix, it doesn't work!
        self._userChats.clear()
        

    # duration: int # important for samples that don't match the interval (at the end of the video when the remaining time isnt divisible by the interval)


    # TODO: activity per second reported on front end like:     activity per second (totalActivityInSample)

    def __post_init__(self):
            self.startTime_text = seconds_to_time(self.startTime)
            self.endTime_text = seconds_to_time(self.endTime)
            self.sampleDuration = self.endTime - self.startTime

@dataclass
class Highlight():
    """Class that stores two samples, a start/end of a noteable section of video
    
    ---

    Attributes:
        start: Sample
            The start Sample corresponding to a highlight.
        end: Sample
            The end Sample corresponding to a highlight.
        length: int
            The length (in seconds) of the highlight. (Calculated based on sample timestamps)
    
    """
    start: Sample
    end: Sample

    # TODO: Figure out best fields to store depending on how we decide to use highlights later


    length: int = field(init=False)

    def __post_init__(self):
        # self.length = self.end.timeStamp? - self.start.timeStamp? 
        raise NotImplementedError 

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

    Attributes:
       [Defined when class Initialized]
        duration: float
            The total duration (in seconds) of the associated video/media. Message times correspond to the video times
        interval: int
            The time interval (in seconds) at which to compress datapoints into samples. (Duration of the samples/How granular the analytics are)
            i.e. at interval=10, each sample's fields contain data about 10 seconds of cumulative data.
            *Only exception is the last sample which may contain less than interval. #TODO: Word this line more clearly
            #(samples in raw_data) is about (video duration/interval) (+1 if necessary to encompass remaining non-divisible data at end of data).
        
        [Automatically Defined on init]
        platform: str
            Used to store the platform the data came from: 'www.youtube.com', 'www.twitch.tv', ...
            While it technically can be determined by the type of subclass, this makes for easier conversion to JSON/output

        [Automatically re-defined on post-init]
        duration_text: str
            String representation of the media duration time.
        interval_text: str
            String representation of the interval time.

        [Defined w/ default and modified DURING analysis]
        mediaTitle: str
            The title of the media associated with the chatlog.
        mediaURL: str
            The link to the media associated with the chatlog (url that it was origianlly downloaded from).
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

        [Defined w/ default and modified AFTER analysis]
        totalUniqueUsers: int
            The total number of unique users that sent a chat message (human users that sent at least one traditional chat)
        overallAvgActivityPerSecond: float
            The average activity per second across the whole chatlog. (totalActivity/totalDuration)
        overallAvgChatMessagesPerSecond: float
            The average number of chat messages per second across the whole chatlog. (totalChatMessages/totalDuration)
        overallAvgUniqueUsersPerSecond: float
            The average number of unique users chatting per second.
    """
    # Defined when class Initialized
    duration: float
    interval: int

    # Automatically Defined on init
    # Because platform has default in the child class, must come after non-defaults above
    platform: str

    # Automatically re-defined on post-init
    duration_text: str = ''
    interval_text: str = ''

    # Defined w/ default and modified DURING analysis
    mediaTitle: str = 'No Media Title'
    mediaURL: str = 'No Media URL'

    samples: List[Sample] = field(default_factory=list)

    totalActivity: int = 0
    totalChatMessages: int = 0
    totalUniqueUsers: int = 0

    # Defined w/ default and modified AFTER analysis
    overallAvgActivityPerSecond: float = 0
    overallAvgChatMessagesPerSecond: float = 0
    overallAvgUniqueUsersPerSecond: float = 0


    # Internal Fields used for calculation but are #NOTE: NOT EXPORTED during json dump (deleted @ post_process)
    _overallUserChats: dict = field(default_factory=dict) # author['id'] -> numChats for full duration
    _currentSample: Sample = None # field(default_factory=None)


    def __post_init__(self):
        self.duration_text = seconds_to_time(self.duration)
        self.interval_text = seconds_to_time(self.interval)
    

    def create_new_sample(self):
        """
        Post-processes the previous sample, then appends & creates a new sample
        following the previous sample sequentially. If a previous sample doesn't exist, 
        creates the first sample.
        
        NOTE: In the current implementation, there could exist consecutive samples with 0 activity 
        (or identical, but less likely), which are easily compressed. However, this uncompressed approach
        makes naively graphing the points easier, which is a primary objective of the output of this program.

        TODO: Implement an option to enable run-length encoding/compression:
                A sequence of identical no-activity samples could eventually be compressed
                into 1 or 3 samples. (3 sample approach helps preserve naive graphing):
                    1 sample apprch: 1 sample consumes all of the consecutive identical samples and modifies
                                        start/end/duration accordingly
                    3 sample apprch: 3 sample approach preserves first and last sample, and combines
                                        intermediate samples. That way the slope into/out of the silence
                                        interval is preserved.
                    Other potential options, but these are the ones we have considered that are not terribly complex
        """

        # We need a new sample, process the last one and create a new sample
        new_sample_start_time = 0 # NOTE: Some chatlogs have chats that start at negative time samples. (Presumably chats right before the video starts). We ignore these for now
        if(self._currentSample != None):
            # process the last sample before creating new one (should have already been appended on creation)
            self._currentSample.sample_post_process()
            new_sample_start_time = self._currentSample.endTime
        
        # New sample end time will not extend past the length of the video
        new_sample_end_time = min(new_sample_start_time + self.interval, self.duration)

        self._currentSample = Sample(startTime=new_sample_start_time, endTime=new_sample_end_time)
        self.samples.append(self._currentSample)


    def process_message(self, msg):
        """Given a msg object from chat, update appropriate statistics based on the chat"""

        msg_time_in_seconds = msg['time_in_seconds']

        if(msg_time_in_seconds < 0 or msg_time_in_seconds > self.duration):
            return # If the message comes before or after the duration of associated media, ignore the msg and don't process it

        # Before processing the msg, make sure that msg belongs with the current sample
        if(self._currentSample == None or msg_time_in_seconds >= self._currentSample.endTime):
            self.create_new_sample() #TODO Pass a NETLOC, so we can create the correct type of subsample

        # Every type of message contributes to total activity
        self.totalActivity += 1
        self._currentSample.activity += 1

        if(msg['message_type']=='text_message'): # text_message is a traditional chat
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


        # NOTE: If there there are only 2 chats, one at time 0:03, and the other at 5:09:12, there are still
        # we still have a lot of empty samples in between (because we still want to graph/track the silence times with temporal stability)

        def to_JSON(self):
            # TODO: Check this...
            return json.dumps(self, indent = 4, default=lambda o: o.__dict__)

    def find_spikes(self):
        """
        Find the spikes in activity in the chatlog based off of the calculated average activities.

        _extended_summary_
        """        
        
        # """"""
        # pass
        # """
        # Finds spikes in the chatlog.
        # A spike is a point in the chatlog where the activity is above a certain threshold.

        # Should be called after the chatlog_post_process() method (after all of the overall averages have been calced)
        # """

    def chatlog_post_process(self):
        """
        After we have finished iterating through the chatlog and constructing all of the samples,
        we call chatlog_post_process() to process the cumulative data points (so we don't have to do this every time we add a sample).

        Also removes the internal fields that don't need to be output in the JSON object.
        """
        print(f"\nDownloaded & Processed {self.totalActivity} messages.")
        print("Post processing...")

        self.totalUniqueUsers = len(self._overallUserChats)

        # NOTE: We calculate actualDuration because if the analyzer is stopped before processing all samples, the duration of the samples does not correspond to the media length
        # This is an unusual case, generally only important when testing, but also keeps in mind future extensibility
        actualDuration = (len(self.samples)-1)*self.interval
        actualDuration += self.samples[-1].sampleDuration

        self.overallAvgActivityPerSecond = self.totalActivity/actualDuration
        self.overallAvgChatMessagesPerSecond = self.totalChatMessages/actualDuration
        # Need to calculate unique users per second based on sample unique users, totalUniqueUsers/duration doesn't tell us what we want to know
        self.overallAvgUniqueUsersPerSecond =  sum(s.avgUniqueUsersPerSecond for s in self.samples)/len(self.samples) 

        # TODO: Calculate more advanced fields like "averageChatsPerUser"

        # Process and remove the final sample from the currentSample field
        self._currentSample.sample_post_process()
        # TODO del doesnt work because it messes with the internal representation of the object which pisses off output for some reason, look into this...
        # del self._currentSample
        # NOTE: delattr didn't do what was required on first attempt but perhaps it was employed incorrectly


        # Spikes are determined after the final averages have been calculated
        self.spikes = self.find_spikes()
        # TODO: Add spikes field to the JSON object and document it as well


        # Remove all other internal variables not suitable for output TODO fix del and do it
        # del self._overallUserChats
        self._overallUserChats.clear()# TODO: Remove this temporary measure
        # del self._currentSample
        self._currentSample = None

        print("Post-processing complete")
        

    # duration: int # important for samples that don't match the interval (at the end of the video when the remaining time isnt divisible by the interval)

    def process_chatlog(self, chatlog: Chat):
        """
        Iterates through the whole chatlog and produces the analytical data

        :param chatlog: The chatlog we have downloaded 
        :type chatlog: chat_downloader.sites.common

        """

        # For debug/tracking
        print("Processing chat log:")
        print("\tCompletion \t Processed Time / Total") # Header for progress stats

        self.mediaTitle = chatlog.title
        # Uses manually added url after the download (non-native field)
        self.mediaURL = chatlog.url
        

        # For each message of all types in the chatlog:
        for idx, msg in enumerate(chatlog):
            if(idx%1000==0 and idx!=0):
                # Progress stats
                print(f"\t({(round((float(msg['time_in_seconds'])/self.duration)*100, 2))}%) \t {msg['time_text']} / {seconds_to_time(self.duration)} \t Processed {idx} messages", end='\r')
                
            self.process_message(msg)

        print(f"\t(100%) \t {seconds_to_time(self.duration)} / {seconds_to_time(self.duration)} \t Processed {self.totalActivity} messages", end='\r')
        # Calculate the [Defined w/ default and modified after analysis] fields of the ChatAnalytics
        self.chatlog_post_process()
@dataclass
class YoutubeChatAnalytics(ChatAnalytics):
    """
    Extension of the ChatAnalytics class, meant to contain data that all chats have
    and data specific to YouTube chats.

    ---

    Attributes:
        [See ChatAnalytics class for common fields]
        # TODO: Add youtube specific fields. Superchats, etc...
    """

    platform: str = YOUTUBE_NETLOC
    
    def process_message(self, msg):
        """Given a msg object from chat, update common fields and youtube-specific fields"""
        super().process_message(msg)
        # TODO: Implement:

    def to_JSON(self):
        # TODO: Check this...
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
@dataclass
class TwitchChatAnalytics(ChatAnalytics):
    """
    Extension of the ChatAnalytics class, meant to contain data that all chats have
    and data specific to Twitch chats.

    ---

    Attributes:
        [See ChatAnalytics class for common fields]
        # TODO: Add twitch specific fields. Superchats, etc...
    """

    platform: str = TWITCH_NETLOC

    def process_message(self, msg):
        """Given a msg object from chat, update common fields and twitch-specific fields"""
        super().process_message(msg)
        # TODO: Implement:
    
    
    def to_JSON(self):
        """
        Returns a JSON string representation of the object

        :return: JSON string representation of the object
        :rtype: str
        """

        # TODO: Check this...
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__)




"""
Main TODO list:

    Stats to track/things to do (not yet implemented) ---
    From most to least important/pressing:
    # TODO: Highest 1,5,10 min periods of engangement (potentially more/different periods) (Highlights)
    # TODO: Local maxima spikes of activity, spikes within certain time of eachother grouped into same highlight (Highlights)
    # TODO: Average messages per chatter (not all users, just average among active chatters) (NOT avg chat per viewers because we don't know how many viewers there are)
    # TODO: Best/(Top 5) chatters.
    # TODO: Median messages per chatter


    # TODO: Go through messsage types to figure out what we should be tracking in the ChatAnalytics

    For Samples:
    # TODO: How many chatters spoke that haven't spoken in the last X samples/minutes/interval? (Not critical)

    # ADVANCED TODO: 
    #   Semantic analysis using DL
    # 
"""


# TODO: Front end advertising:
"""
For creators: don't forget to subscribe effective? what is most engaging part of stream?

For editors: more quickyl find interesting parts

potential creators:
    pick popular youtube/twitch streamers, see what part of their streams generate the most engagement

Researchers
"""