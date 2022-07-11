import json
from argparse import ArgumentTypeError
from dataclasses import dataclass,field
from abc import ABC, abstractclassmethod
from chat_downloader.sites.common import Chat
from typing import List
import logging

from chat_downloader.utils.core import seconds_to_time

# TODO:
# The platforms we currently support downloading from.
# Each has a corresponding ChatAnalytics extension with site-specific behavior
YOUTUBE_NETLOC = 'www.youtube.com'
TWITCH_NETLOC = 'www.twitch.tv'
SUPPORTED_PLATFORMS = [YOUTUBE_NETLOC, TWITCH_NETLOC]

# NOTE: Yes CamelCased fields are unpythonic, but the primary intention is to convert these dataclasses into JSON objects and it is one less step to handle then!

"""
Xenonva's chat-downloader stores each message (a 'chat item' in their vernacular)
as a dictionary. (*almost) All messages contain certain fields in common, 

See for more info: https://chat-downloader.readthedocs.io/en/latest/items.html#chat-item-fields

All messages regardless of their type are considered activity.

"""


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

        --- TODO: Below not yet implemented ---

        bestChatters:
            #TODO: Figure out how to type-define (or not) the author of a message, and how we want to store them in a list
            # NOTE: See https://death.andgravity.com/dataclasses about typeless dataclass stuff

        # TODO: Add   
        # . . . (total/Avg superchats, newMembers, etc... (need to check YT/Twitch/Xenova docs to see what possible message types we can track are))
        # . . . (total/Average of each datapoint)

        # TODO: Add
            longest-1-min-sustained, 5 min, etc... and similar super-interval temporaily aware anlysis


        # Fields only calculated if we want advanced statistics: TODO
        # TODO: average chats per viewer

        # TODO: Median chats per viewer
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
        Post-processes the previous sample , and appends+creates a new sample
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

        # TODO: replace totalActivity/totals/overall with incrementing samples, then add sample stuff
        #       to the total once at the end to prevent unnecessary code duplication

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

        
        
        # If the sample is added, perform updated calculations to avg and stuff.
                    
        # TODO: We have to add in appropriate amount of empty samples between two messages that are more than a sample length apart
        # print (msg['message'])


        # NOTE: If there there are only 2 chats, one at time 0:03, and the other at 5:09:12, there are still
        # we still have a lot of empty samples in between (because we still want to graph/track the silence times with temporal stability)
        # 
        # if there is a period with 0 chats in a normal stream, we want to explicitly record that period as 0

        # We still take a sample so we 

        # option to enable run-length encoding
            """
        #TODO: THIS IS THE NEXT THING TO TACKLE!

        Logic in process_message should be:

        If the receieved message should be in the sample we are currently building, add it to that
            # TODO: implement an addMsg() method to sample to easily add a sample object from a msg
            #            ^ is NOT the same as a sample constructor b/c there should be multiple msgs in a single sample

        If it doesnt belong in the current sample, build a new empty sample at the next appropriate timeframe

            If the new message's timestamp STILL doesn't belong in the curr sample, increment again to a new empty sample.
            We increment until it fits then add it to the appropriate sample

        # TODO: Alternatively, find a way to replace a long string of empty samples with a start/end empty sample
                think in the morning with more sleep
        

        Need to ensure that the last sample(s) gets added automatically when there are no more chats
            Think of case where there is one chat very early on in stream and 0 chats for the rest
            of stream

        """
        def to_JSON(self):
            # TODO: Check this...
            return json.dumps(self, indent = 4, default=lambda o: o.__dict__)

    def chatlog_post_process(self):
        """
        After we have finished iterating through the chatlog and constructing all of the samples,
        we call chatlog_post_process() to process the cumulative data points (so we don't have to do this every time we add a sample).

        Also removes the internal fields that don't need to be output in the JSON object.
        """
        print(f"\nProcessed {self.totalActivity} messages.")
        print("Post processing...")

        self.totalUniqueUsers = len(self._overallUserChats)

    
        # NOTE: We calculate actualDuration because if the analyzer is stopped before processing all samples, the duration of the samples does not correspond to the media length
        # This is an unusual case, generally only important when testing, but also keeps in mind future extensibility
        actualDuration = (len(self.samples)-1)*self.interval
        actualDuration += self.samples[-1].sampleDuration

        self.overallAvgActivityPerSecond = self.totalActivity/actualDuration
        self.overallAvgChatMessagesPerSecond = self.totalChatMessages/actualDuration
        # Need to calculate unique users per second based on sample unique users, totalUniqueUsers/duration doesn't tell us anything meaningful 
        self.overallAvgUniqueUsersPerSecond =  sum(s.avgUniqueUsersPerSecond for s in self.samples)/len(self.samples) 


        # TODO: Calculate more advanced fields like "averageChatsPerUser"

        # Process and remove the final sample
        self._currentSample.sample_post_process()
        # TODO del doesnt work because it messes with the internal representation of the object which pisses off output for some reason, look into this...
        # del self._currentSample
        # NOTE: delattr didn't do what was required on first attempt but perhaps it was employed incorrectly

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
        print("\tCompletion \t Processed Time / Total")

        self.mediaTitle = chatlog.title
        # Uses manually added url after the download (non-native field)
        self.mediaURL = chatlog.url
        

        # For each message of all types in the chatlog:
        for idx, msg in enumerate(chatlog):
            # For debug/tracking

            # float(msg['time_in_seconds'])
            if(idx%1000==0 and idx!=0):
                # print("\t (%d) %s / %s  | Processed %d messages" % (float(msg['time_in_seconds']) ,msg['time_text'], seconds_to_time(self.duration), idx), end='\r')
                
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
        # print(f"TODO: youtube specific fields process msg")
        # print(f"this gets called to update the youtube specific fields ")
        # print(msg)
        # raise NotImplementedError
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
        # print(f"this gets called to update the twitch specific fields {msg}")
        # raise NotImplementedError
        # TODO: Implement:

        # TODO: Detect local maxima spikes (even if below average) (sharp & sustained changes from one sample to next)
    


        # msg[NORMAL_MESSAGE[TWITCH_NETLOC]]
        # msg["text_message"]


        # # TODO: define mapping from:
        # #   NORMAL_MESSAGE: {
        # #       YOUTUBE_NETLOC : "text_message"  
        # #       TWITCH_NETLOC : "text_message"                  
        # # }
        # #   
    
    def to_JSON(self):
            # TODO: Check this...
            return json.dumps(self, indent = 4, default=lambda o: o.__dict__)


# print(dict(sorted(userChatCount.items(), key=lambda item: item[1])))

# Track highest engagement, instead raw number of messages per interval, number of unique chatters 
# per interval

# Track average number of chats sent by a single user

# chatLogJSONFile.close()

# numberofchattersmakingtheirfirstchat of the stream
# numberOfChattersThatSpokeJustNowThatHaventSpokenInPastXInterval . . .




    # def __init__(self):
    #     """Instantiates the fields with default values"""
    #     self.platform = None #Should be overriden by the subclass constructor
    #     self.interval = 0 
    #     self.samples = []
    #     self.duration = 0
        

    # def toJSON():
    #     # TODO: Convert the snake case fields to camel case
    #     print("TODO: Implement")




# highlights

# ADVANCED TODO: Semantic analysis using DL

#ad : for creators:
#   dont forget to subscribe effective?

# ad for editors:

# potential creators:
#        pick popular youtube/twitch streamers, see what part of their streams generate the most engagement

# researchers:
#       




# TODO: Go through messsage types to figure out what we should be tracking in the ChatAnalytics

# _YT_MESSAGE_GROUPS = {
#         'messages': [
#             'text_message'  # normal message
#         ],
#         'superchat': [
#             # superchat messages which appear in chat
#             'membership_item',
#             'paid_message',
#             'paid_sticker',
#         ],
#         'tickers': [
#             # superchat messages which appear ticker (at the top)
#             'ticker_paid_sticker_item',
#             'ticker_paid_message_item',
#             'ticker_sponsor_item',
#         ],
#         'banners': [
#             'banner',
#             'banner_header'
#         ],

#         'donations': [
#             'donation_announcement'
#         ],
#         'engagement': [
#             # message saying live chat replay is on
#             'viewer_engagement_message',
#         ],
#         'purchases': [
#             'purchased_product_message'  # product purchased
#         ],

#         'mode_changes': [
#             'mode_change_message'  # e.g. slow mode enabled
#         ],

#         'deleted': [
#             'deleted_message'
#         ],
#         'bans': [
#             'ban_user'
#         ],

#         'placeholder': [
#             'placeholder_item'  # placeholder
#         ]
#     }


# _TWITCH_MESSAGE_GROUPS = {
#     'messages': [
#         'text_message'
#     ],
#     'bans': [
#         'ban_user'
#     ],
#     'deleted_messages': [
#         'delete_message'
#     ],
#     'hosts': [
#         'host_target'
#     ],
#     'room_states': [
#         'room_state'
#     ],
#     'user_states': [
#         'user_state'
#     ],
#     'notices': [
#         'user_notice',
#         'notice',
#         'successful_login'
#     ],
#     'chants': [
#         'crowd_chant'
#     ],
#     'other': [
#         'clear_chat',
#         'reconnect'
#     ]
# }

# _TWITCH_MESSAGE_GROUP_REMAPPINGS = {
#         # TODO add rest of
#         # https://dev.twitch.tv/docs/irc/msg-id

#         'messages': {
#             'highlighted-message': 'highlighted_message',
#             'skip-subs-mode-message': 'send_message_in_subscriber_only_mode',
#         },
#         'bits': {
#             'bitsbadgetier': 'bits_badge_tier',
#         },
#         'subscriptions': {
#             'sub': 'subscription',
#             'resub': 'resubscription',
#             'subgift': 'subscription_gift',
#             'anonsubgift': 'anonymous_subscription_gift',
#             'anonsubmysterygift': 'anonymous_mystery_subscription_gift',
#             'submysterygift': 'mystery_subscription_gift',
#             'extendsub': 'extend_subscription',

#             'standardpayforward': 'standard_pay_forward',
#             'communitypayforward': 'community_pay_forward',
#             'primecommunitygiftreceived': 'prime_community_gift_received',
#         },
#         'upgrades': {
#             'primepaidupgrade': 'prime_paid_upgrade',
#             'giftpaidupgrade': 'gift_paid_upgrade',
#             'rewardgift': 'reward_gift',
#             'anongiftpaidupgrade': 'anonymous_gift_paid_upgrade',
#         },
#         'raids': {
#             'raid': 'raid',
#             'unraid': 'unraid'
#         },
#         'hosts': {
#             'host_on': 'start_host',
#             'host_off': 'end_host',
#             'bad_host_hosting': 'bad_host_hosting',
#             'bad_host_rate_exceeded': 'bad_host_rate_exceeded',
#             'bad_host_error': 'bad_host_error',
#             'hosts_remaining': 'hosts_remaining',
#             'not_hosting': 'not_hosting',

#             'host_target_went_offline': 'host_target_went_offline',
#         },
#         'rituals': {
#             'ritual': 'ritual',
#         },
#         'room_states': {
#             # slow mode
#             'slow_on': 'enable_slow_mode',
#             'slow_off': 'disable_slow_mode',
#             'already_slow_on': 'slow_mode_already_on',
#             'already_slow_off': 'slow_mode_already_off',

#             # sub only mode
#             'subs_on': 'enable_subscriber_only_mode',
#             'subs_off': 'disable_subscriber_only_mode',
#             'already_subs_on': 'sub_mode_already_on',
#             'already_subs_off': 'sub_mode_already_off',

#             # emote only mode
#             'emote_only_on': 'enable_emote_only_mode',
#             'emote_only_off': 'disable_emote_only_mode',
#             'already_emote_only_on': 'emote_only_already_on',
#             'already_emote_only_off': 'emote_only_already_off',

#             # r9k mode
#             'r9k_on': 'enable_r9k_mode',
#             'r9k_off': 'disable_r9k_mode',
#             'already_r9k_on': 'r9k_mode_already_on',
#             'already_r9k_off': 'r9k_mode_already_off',

#             # follower only mode
#             'followers_on': 'enable_follower_only_mode',
#             'followers_on_zero': 'enable_follower_only_mode',  # same thing, handled in parse
#             'followers_off': 'disable_follower_only_mode',
#             'already_followers_on': 'follower_only_mode_already_on',
#             'already_followers_on_zero': 'follower_only_mode_already_on',
#             'already_followers_off': 'follower_only_mode_already_off',

#         },
#         'deleted_messages': {
#             'msg_banned': 'banned_message',

#             'bad_delete_message_error': 'bad_delete_message_error',
#             'bad_delete_message_broadcaster': 'bad_delete_message_broadcaster',
#             'bad_delete_message_mod': 'bad_delete_message_mod',
#             'delete_message_success': 'delete_message_success',
#         },
#         'bans': {

#             # ban
#             'already_banned': 'already_banned',
#             'bad_ban_self': 'bad_ban_self',
#             'bad_ban_broadcaster': 'bad_ban_broadcaster',
#             'bad_ban_admin': 'bad_ban_admin',
#             'bad_ban_global_mod': 'bad_ban_global_mod',
#             'bad_ban_staff': 'bad_ban_staff',
#             'ban_success': 'ban_success',

#             # unban
#             'bad_unban_no_ban': 'bad_unban_no_ban',
#             'unban_success': 'unban_success',

#             'msg_channel_suspended': 'channel_suspended_message',

#             # timeouts
#             'timeout_success': 'timeout_success',

#             # timeout errors
#             'bad_timeout_self': 'bad_timeout_self',
#             'bad_timeout_broadcaster': 'bad_timeout_broadcaster',
#             'bad_timeout_mod': 'bad_timeout_mod',
#             'bad_timeout_admin': 'bad_timeout_admin',
#             'bad_timeout_global_mod': 'bad_timeout_global_mod',
#             'bad_timeout_staff': 'bad_timeout_staff',
#         },
#         'mods': {
#             'bad_mod_banned': 'bad_mod_banned',
#             'bad_mod_mod': 'bad_mod_mod',
#             'mod_success': 'mod_success',
#             'bad_unmod_mod': 'bad_unmod_mod',
#             'unmod_success': 'unmod_success',
#             'no_mods': 'no_mods',
#             'room_mods': 'room_mods',
#         },
#         'colours': {
#             'turbo_only_color': 'turbo_only_colour',
#             'color_changed': 'colour_changed',
#         },
#         'commercials': {
#             'bad_commercial_error': 'bad_commercial_error',
#             'commercial_success': 'commercial_success',
#         },

#         'vips': {
#             'bad_vip_grantee_banned': 'bad_vip_grantee_banned',
#             'bad_vip_grantee_already_vip': 'bad_vip_grantee_already_vip',
#             'vip_success': 'vip_success',
#             'bad_unvip_grantee_not_vip': 'bad_unvip_grantee_not_vip',
#             'unvip_success': 'unvip_success',
#             'no_vips': 'no_vips',
#             'vips_success': 'vips_success',
#         },
#         'chants': {
#             'crowd-chant': 'crowd_chant'
#         },
#         'charity': {
#             'charity': 'charity'
#         },
#         'other': {
#             'cmds_available': 'cmds_available',
#             'unrecognized_cmd': 'unrecognized_cmd',
#             'no_permission': 'no_permission',
#             'msg_ratelimit': 'rate_limit_reached_message',
#         }
#     }