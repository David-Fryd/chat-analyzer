import json
import logging

from chat_downloader import ChatDownloader
from urllib.parse import urlparse
from chat_downloader.sites.common import Chat
from dataformat import * # YoutubeChatAnalytics, TwitchChatAnalytics


# Times in seconds dictating how granular the interval can be (how long the individual samples are)
MAX_INTERVAL = 120
MIN_INTERVAL = 1


def download_chatlog(url: str):
    """
    Downloads and returns the chat log using Xenonva's chat-downloader
    
    :param url: The URL of the past stream/VOD to download the chat from
    :param type: str
    :returns: The chatlog we have downloaded
    :rtype: chat_downloader.sites.common.Chat
    """

    # Define the arguments for getting the chatlog using chat-downloader
    chat_download_settings =  {
        "url" : url,
        "message_types" : 'all'
    }

    print("Getting chatlog using Xenonva's chat-downloader (https://github.com/xenova/chat-downloader)...")

    try:
        chat = ChatDownloader().get_chat(
            chat_download_settings['url'], 
            message_types=[chat_download_settings['message_types']])       # create a generator
    except Exception as exception:
        logging.critical("ERORR: Could not get chat: "+ str(exception))
        exit(1)

    print("Successfully retrieved chat generator:")
    print("\tTitle: %s" % (str(chat.title)))
    print("\tDuration: %s (%s seconds)" % (seconds_to_time(chat.duration), str(chat.duration)))
    print("""\t\033[1;33mNOTICE: Downloading chats is the largest rate-limiting factor.
             \t\033[0;33mIf you intend to sample the data differently multiple times, consider using \033[1;33mchatfile\033[0;33m mode.\n\033[0m""")

    return chat

def check_chatlog_supported(chatlog: Chat, url: str):
    """
    Ensures that we are able to properly analyze the downloaded chatlog by
    enforcing the metadata matches expected values. 
    (Our own logic depends on certain things being true)

    If there is a breach of compliance, we exit (we consider this to be a fatal error)
    
    :param chatlog: The chatlog we have downloaded
    :type chatlog: chat_downloader.sites.common.Chat
    :param url: The URL of the video we have downloaded the log from
    :type url: str

    Currently we ensure:
        - The video/stream happened in the past (not currently live or scheduled)
        - The chat is downloaded from a supported platform that we have a proper
        way of parsing.
    """

    if(chatlog.status !='past'):
        logging.critical("ERROR: chat-analyzer does not support live or upcoming streams. Wait until the stream is over to use this tool!")
        exit(1)
    if(chatlog.status == None):
        logging.critical(f"ERROR: unrecognized stream status: {chatlog.status}. chat-analyzer must be able to confirm that the stream is over")
        exit(1)
    
    # NOTE: I don't currently know of a way to get the platform from the chatlog itself, so a quick operation here is a simple-enough solution
    platform = urlparse(url).netloc
    if(platform not in SUPPORTED_PLATFORMS):
        # NOTE: This is for platforms that the chat-downloader can handle but chat-analyzer can't
        logging.critical(f"ERROR: chat-analyzer does not currently support chatlogs from {platform}")
        exit(1)

def run(**kwargs):
    """Runs the chat-analyzer
    
    :param url: The URL of the past stream/VOD we want to download and analyze
    :type url: str
    :param interval: The size of each sample in seconds (granularity of the analytics)
    :type interval: int
    :returns: The chat analytics data as a dataclass
    :rtype: dataformat.ChatAnalytics (dataformat.YoutubeChatAnalytics or dataformat.TwitchChatAnalytics)
    """

    # Interpret and extract CLI arguments from kwargs
    for arg in kwargs:
        value = kwargs[arg]
        print(f"analyzing arg {arg}: {value}")

    source = kwargs.get('source') # Is either a url, or a json filepath that is raw chat data or an already processed output file...
    interval = kwargs.get('interval')

    print_interval = kwargs.get('print_interval')

    mode = kwargs.get('mode')

    # Check interval argument, we check the url arg's platform in check_chatlog_supported()
    # NOTE: We double check here in addition to in CLI
    if(interval > MAX_INTERVAL or interval < MIN_INTERVAL): 
        raise ValueError(f"Sample interval must be {MIN_INTERVAL} <= interval <= {MAX_INTERVAL}")

    # Get the chat using the chat downloader and ensure that we can work with that data
    chatlog: Chat
    if(mode=='url'):
        url = source
        chatlog = download_chatlog(url)
        check_chatlog_supported(chatlog, url)
    else:
        raise NotImplementedError(f"Mode {mode} is not yet supported... oops :(")

    # Next section: Create the proper type of ChatAnalytics object based on the platform
    chatAnalytics: ChatAnalytics
    duration = chatlog.duration
    platform = urlparse(url).netloc

    if(platform == YOUTUBE_NETLOC):
        chatAnalytics = YoutubeChatAnalytics(duration=duration, interval=interval)
    elif(platform == TWITCH_NETLOC):
        chatAnalytics = TwitchChatAnalytics(duration=duration, interval=interval)
    else:
        logging.critical(
            "ERROR: No corresponding ChatAnalytics object.\n\
            NOTE: Should have caught this in supported platforms checks earlier...")
        exit(1)

    # Now, we can process the data!
    chatAnalytics.process_chatlog(chatlog, url, print_interval)
        
    # chatAnalytics now contains all analytical data. We can print/return as ncessary
   
    jsonObj = chatAnalytics.to_JSON()
    
    output_filepath:str ='output/'+chatlog.title+'.json'
    if(kwargs.get('output')):
        output_filepath = kwargs.get('output')


    with open(output_filepath, 'w') as f:
        json.dump(json.loads(jsonObj), f, ensure_ascii=False, indent=4)
    
    print(f"Successfully wrote chat analytics to {output_filepath}")
    
    return chatAnalytics
