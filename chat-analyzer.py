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

    # TODO: Print information more intelligently (and selectively based on arguments) (using logging) instead of regular print statements
    print("Getting chatlog using Xenonva's chat-downloader (https://github.com/xenova/chat-downloader)...")

    try:
        chat = ChatDownloader().get_chat(
            chat_download_settings['url'], 
            message_types=[chat_download_settings['message_types']])       # create a generator
        # Manually adds a url field to the Chat object
        chat.url = url
    except Exception as exception:
        # TODO: Print errors more intelligently (using logging or to stderr) instead of regular print statements
        logging.critical("ERORR: Could not get chat: "+ str(exception))
        exit(1)
        # TODO: Figure out how to use the specific exception generated by ChatDownloader to inform an error code 
        # (or figure out a way to intelligently pass it up a pipeline so it can be communicated to client if this was run on the server)


    # TODO: Print information more intelligently (and selectively based on arguments) (using logging) instead of regular print statements
    print("Successfully retrieved chat generator:")
    print("\tTitle: %s" % (str(chat.title)))
    print("\tDuration: %s (%s seconds)" % (seconds_to_time(chat.duration), str(chat.duration)))
    print("\t\033[1;33mNOTICE: generator from chat-downloader is currently largest rate-limiting factor.\n\t\033[0;33mTODO: Figure out ways to circumvent/separate rate-limiting factors.\033[0m")

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

    # TODO: Define more intelligent exit codes that are meaningful to observers not reading logs or stderr/output
    # TODO: Print errors more intelligently (using logging or to stderr) instead of regular print statements
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


# TODO: interval and url are determined from argparse and given to this function here
def run(url: str, interval: int):
    """Runs the chat-analyzer
    
    :param url: The URL of the past stream/VOD we want to download and analyze
    :type url: str
    :param interval: The size of each sample in seconds (granularity of the analytics)
    :type interval: int

    #TODO: Define return(s) and rtype docs
    
    """

    # Check interval argument, we check the url arg's platform in check_chatlog_supported()
    if(interval > MAX_INTERVAL or interval < MIN_INTERVAL):
        raise ValueError(f"Sample interval must be {MIN_INTERVAL} <= interval <= {MAX_INTERVAL}")

    # Get the chat using the chat downloader and ensure that we can work with that data
    chatlog: Chat = download_chatlog(url)
    check_chatlog_supported(chatlog, url)

    # Next section: Create the proper type of ChatAnalytics object based on the platform
    chatAnalytics: ChatAnalytics
    duration = chatlog.duration
    platform = urlparse(url).netloc

    if(platform == YOUTUBE_NETLOC):
        chatAnalytics = YoutubeChatAnalytics(duration=duration, interval=interval)
    elif(platform == TWITCH_NETLOC):
        chatAnalytics = TwitchChatAnalytics(duration=duration, interval=interval)
    else:
        logging.critical( # TODO: print statement format and better error codes
            "ERROR: No corresponding ChatAnalytics object.\n\
            NOTE: Should have caught this in supported platforms checks earlier...")
        exit(1)

    # Now, we can process the data!
    chatAnalytics.process_chatlog(chatlog)
        
    # chatAnalytics now contains all analytical data. We can print/return as ncessary
    print("---")
    print("---")

    # Temporary null of the internal variables here so they arent printed, TODO: REMOVE
    chatAnalytics._userChats = None

    # print(chatAnalytics)

    jsonObj = chatAnalytics.to_JSON()
    # print(jsonObj)
    with open('markiplier.json', 'w') as f:
        json.dump(json.loads(jsonObj), f, ensure_ascii=False, indent=4) 

    """
    analyticsJSONObj = jsonpickle.encode(chatAnalytics, unpicklable=False)
    
    print("\n\n\n\n\n\n\n\n\nJSON OBJ:")
    analyticsJSONData = json.dumps(analyticsJSONObj, indent=4)
    print(analyticsJSONData)

    with open('analytics.json', 'w') as f:
        json.dump(analyticsJSONObj, f, ensure_ascii=False, indent=4)

    with open('analytics2.txt', 'w') as f:
        json.dump(analyticsJSONObj, f, ensure_ascii=False, indent=4)
    """
    
    # TODO: When returned, the method that gets it should decide how to output it based on CLI
    return chatAnalytics


# TODO: This gets called from another file that takes in arguments and passes them to run.
# For testing purposes we just call it here internally


# Some testing URLs
# TODO: Replace url with argparse arg
url = 'https://www.youtube.com/watch?v=97w16cYskVI' # yt stream that comes with lots of message types (retrieved from chat-downloader testing sample) TODO: [blocked now?! check into]
# url = 'asdds.com/a/b/c/d' # (error) invalid URL
# url = 'https://www.youtube.com/watch?v=5qap5aO4i9A' # (error) stream still live (lo-fi hip hop girl runs 24/7)
# url = 'https://www.twitch.tv/videos/1522574868'  # summit1g's 14 hour stream
# url = 'https://www.youtube.com/watch?v=PTWpoZITraE&ab_channel=RobScallon' # (error) Youtube video without chat replay
# url = 'https://www.youtube.com/watch?v=UR902_1LhVk&t=24333s&ab_channel=Ludwig' # Ludwig's 1 million dollar game poker stream, 8:57:25, 158366 totalActivity
# url = 'https://www.youtube.com/watch?v=vjBNozL9Daw' #(error for now TODO: test later) no chat replay
url = 'https://www.twitch.tv/videos/1289325547'


run(url=url, interval=5)


