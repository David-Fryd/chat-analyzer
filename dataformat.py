from argparse import ArgumentTypeError
from dataclasses import dataclass,field
from abc import ABC, abstractclassmethod
from typing import List

# TODO:
# The platforms we currently support downloading from.
# Each has a corresponding ChatAnalytics extension with site-specific behavior
YOUTUBE_NETLOC = 'www.youtube.com'
TWITCH_NETLOC = 'www.twitch.tv'
SUPPORTED_PLATFORMS = [YOUTUBE_NETLOC, TWITCH_NETLOC]

@dataclass
class Sample():
    #TODO: Implement
    """
    Class that contains...
    
    ---

    Attributes:
    
    """
    duration: int # important for samples that don't match the interval (at the end of the video when the remaining time isnt divisible by the interval)


    def __post_init__(self):
            # self.length = self.end.timeStamp? - self.start.timeStamp? 
            raise NotImplementedError 

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
       [Defined when Initialized]
        duration: str
            The duration of the associated video in seconds. Message times correspond to the video times
        interval: int
            The time interval (in seconds) that a single sample of data uses. (How granular the analytics are)
            i.e. at interval=10, each sample's fields contain data about 10 seconds of cumulative data.
            *Only exception is the last sample which may contain less than interval. #TODO: Word this line more clearly
            #(samples in raw_data) is about (video duration/interval) (+1 if necessary to encompass remaining non-divisible data at end of data).
        
        [Automatically Defined on init]
        platform: str
            Used to store the platform the data came from: 'www.youtube.com', 'www.twitch.tv', ...
            While it technically can be determined by the type of subclass, this makes for easier conversion to JSON/output

        [Defined w/ default and modified during analysis]
        samples: List[Sample]
            An array of sequential samples, each corresponding to data about a section of chat of 'interval' seconds long.
            Each sample has specific data corresponding to a time interval of the vid. See 'class Sample()'
        totalActivity: int
            The total number of messages/things (of any type!) that appeared in chat. (Sum of intervalActivity from all samples) 
            Includes messages,notifications,subscriptions, superchats, . . . *anything* that appeared in chat
        averageActivity: int
            The average intervalActivity for all samples. (totalActivity/len(samples))
        totalChatMessages: int
            The total number of chats sent by human (non-system) users (what is traditionally thought of as a chat)
            NOTE: Difficult to discern bots from humans other than just creating a known list of popular bots and blacklisting, 
            because not all sites (YT/Twitch) provide information on whether chat was sent by a registered bot or not.


        # TODO: Implement
        uniqueChatters: int
            The total number of unique chatters that sent a 'chat message' during the stream.
            (i.e. human users that sent a traditional chat)

        # TODO: average chats per viewer

        bestChatters:
            #TODO: Figure out how to type-define (or not) the author of a message, and how we want to store them in a list
            # NOTE: See https://death.andgravity.com/dataclasses about typeless dataclass stuff

        # TODO: Add   
        # . . . (total/Avg superchats, newMembers, etc... (need to check YT/Twitch/Xenova docs to see what possible message types we can track are))
        # . . . (total/Average of each datapoint)

        # TODO: Add
            longest-1-min-sustained, 5 min, etc... and similar super-interval temporaily aware anlysis

        # NOT YET IMPLEMENTED: [Determined after recalculation pass (2nd pass over the dataclass, not the raw data)]
    """
    # Defined when Initialized
    duration: int
    interval: int

    # Automatically Defined on init
    # Because platform has default in the child class, must come after non-defaults above
    platform: str

    # Defined w/ default and modified during analysis
    samples: List[Sample] = field(default_factory=list)

    totalActivity: int = 0
    averageActivity: int = 0
    
    totalChatMessages: int = 0
    averageChatMessages: int = 0
   
    uniqueChatters: int = 0
    
    def process_message(self, msg):
        """Given a msg object from chat, update appropriate variables based on the chat"""
        print(f"parent specific fields process msg {msg}")
        raise NotImplementedError
        # TODO: Implement:
    


    # def __init__(self):
    #     """Instantiates the fields with default values"""
    #     self.platform = None #Should be overriden by the subclass constructor
    #     self.interval = 0 
    #     self.samples = []
    #     self.duration = 0
        

    # def toJSON():
    #     # TODO: Convert the snake case fields to camel case
    #     print("TODO: Implement")

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
        print(f"this gets called to update the youtube specific fields {msg}")
        raise NotImplementedError
        # TODO: Implement:

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
        print(f"this gets called to update the twitch specific fields {msg}")
        raise NotImplementedError
        # TODO: Implement:



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