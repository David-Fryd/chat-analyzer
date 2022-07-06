import json
import logging
from chat_downloader import ChatDownloader
from urllib.parse import urlparse
from dataformat import * # YoutubeChatAnalytics, TwitchChatAnalytics



# # TODO:
# if(interval > self.MAX_INTERVAL or interval < self.MIN_INTERVAL):
#             raise ValueError(f"Sample interval must be {self.MIN_INTERVAL} <= interval <= {self.MAX_INTERVAL}")
#             # TODO: Check to ensure this is the proper way to pass a custom message to an exception

# TODO : dataclasses go here

# TODO: Define sample class

#  chat_downloader "https://www.youtube.com/watch?v=97w16cYskVI" --output newwithsuper.txt --message_types all

# TODO: Instead of writing to a big JSON file, can we analyze
# on message at a time to avoid the big JSON file? (Document this)

# TODO: fix all of the janky error messages, decide whether to use logging/print/whatever 

# TODO: Replace url with argparse arg
# url = 'https://www.youtube.com/watch?v=5qap5aO4i9A'
# url = 'https://www.youtube.com/watch?v=97w16cYskVI'
url = 'https://www.youtube.com/watch?v=97w16cYskVI'
# url = 'asdds.com/a/b/c/d'
url = 'https://www.twitch.tv/videos/1522574868'
print("Getting chat using Xenonva's chat-downloader (https://github.com/xenova/chat-downloader):")

chat = None

# Define the CLI arguments for getting chats
chat_download_settings =  ("%s %s" % (url, '--max_messages MAX_MESSAGES'))

try:
    chat = ChatDownloader().get_chat(url, message_types=['all'])       # create a generator
except Exception as exception:
    # print("[ERROR DOWNLOADING CHAT]: "+ str(exception))
    logging.critical("ERORR: Could not get chat: "+ str(exception))
    exit(1)


print(f"Status: {chat.status}")
if(chat.status == None):
    print("Unknwon error getting chat status")
    exit(1)

if(str(chat.status) !='past'):
    logging.critical("ERROR: chat-analyzer does not support live or upcoming streams, wait until the stream is over to use this tool!")
    exit(1)

print("Successfully retrieved chat:")
print("\tTitle: %s" % (str(chat.title)))
print("\tDuration: %s" % (str(chat.duration)))
# We must manually determine website because the chat-downloader provides no easy way of
# dynamically determining the source of the chats (does not expose easily). In order
# to maintain as much integrity of the original chat-downloader dependency codebase for
# maintenance-purposes, we do a bit of extra easy work here.
website = urlparse(url).netloc
print(f"\twebsite: {website}")

print(SUPPORTED_PLATFORMS)

RYT = YoutubeChatAnalytics(duration=chat.duration, interval=5)
RTWITCH = TwitchChatAnalytics(duration=chat.duration, interval=5)

RYT.process_message("ABCDEFG")
RTWITCH.process_message("abcdef")

print(RYT.platform)
print(RTWITCH.platform)


exit(0) #TEMP TODO: REMOVE
 



# print(str(chat.duration))
    

# for message in chat:                        # iterate over messages
#     chat.print_formatted(message)           # print the formatted message

# # Testing hardcoded file path
# chatFilePath: str = 'localtestJSON/mixedData.json'

# # Open JSON File
# chatLogJSONFile = open(chatFilePath)

# # returns JSON object as 
# # a dictionary
# data = json.load(chatLogJSONFile)



# Testing sets in python
seenMessageTypes = set()

# Testing dictionary map in python
userChatCount = {}
maxAuthorData = {}
maxAuthorChatNumber = 0




# Iterate through JSON list
for idx,msg in enumerate(chat):
    if(idx%1000==0 and idx!=0):
        print("Processed %d messages" % (idx))
        logging.debug("Processed %d messages" % (idx))

    # print(msg['message_type'])

    # print("FullMessage #%d: %s\n" % (idx,msg))

    # print("Action type: %s" % (msg['action_type'])) 

    msgType = msg['message_type']
    if(msgType not in seenMessageTypes):
        # print("%s added to seenMessageTypes" % (msgType))
        # Having the add under the check is redundant but we need it anyway for the print
        seenMessageTypes.add(msgType)

    if(msgType=='resubscription'):
        print("RESUB AT " + msg['time_text'])
        print()

    # TODO: Enable advanced/simple mode, advanced will not bother will user statistics
    # which will run faster

    # if 'author' in msg:
    #     author = msg['author']
    #     # print(author['name'])
    #     # print(author['id'])

    #     authID = author['id']

    #     if(msg['message_type']=="text_message"):
    #         if authID in userChatCount:
    #             userChatCount[authID] += 1
    #         else:
    #             userChatCount[authID] = 1

    #         # update max if necessary
    #         if(userChatCount[authID] > maxAuthorChatNumber):
    #             maxAuthorChatNumber = userChatCount[author['id']]
    #             maxAuthorData = author

    #     # # If you want to isolate out a user
    #     # if(authID=='UC9_dMgvP46Jbt5WF1dYvZPg'):
    #     #     print(msg['message'])



    # if(idx==500):
    #     break

print("Seen message types:")
print(seenMessageTypes)

print("")

print("Biggest chatter: %s" % (maxAuthorData['name']))
print(maxAuthorData)
print("Number of chats: %d" % (maxAuthorChatNumber))
print("Number of unique chatters: %d" % (len(userChatCount)))

# random stuff:

# print(dict(sorted(userChatCount.items(), key=lambda item: item[1])))

# Track highest engagement, instead raw number of messages per interval, number of unique chatters 
# per interval

# Track average number of chats sent by a single user

# chatLogJSONFile.close()

# numberofchattersmakingtheirfirstchat of the stream
# numberOfChattersThatSpokeJustNowThatHaventSpokenInPastXInterval . . .

# highlights

# ADVANCED TODO: Semantic analysis using DL

#ad : for creators:
#   dont forget to subscribe effective?

# ad for editors:

# potential creators:
#        pick popular youtube/twitch streamers, see what part of their streams generate the most engagement

# researchers:
#       