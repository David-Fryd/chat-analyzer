import json
import logging

# Testing hardcoded file path
chatFilePath: str = 'localtestJSON/mixedData.json'

# Open JSON File
chatLogJSONFile = open(chatFilePath)

# returns JSON object as 
# a dictionary
data = json.load(chatLogJSONFile)


# Testing sets in python
seenMessageTypes = set()

# Testing dictionary map in python
userChatCount = {}
maxAuthorData = {}
maxAuthorChatNumber = 0

# Iterate through JSON list
for idx,msg in enumerate(data):
    # print("FullMessage #%d: %s\n" % (idx,msg))

    # print("Action type: %s" % (msg['action_type'])) 

    if 'author' in msg:
        author = msg['author']
        # print(author['name'])
        # print(author['id'])

        authID = author['id']

        if authID in userChatCount:
            userChatCount[authID] += 1
        else:
            userChatCount[authID] = 1

        # update max if necessary
        if(userChatCount[authID] > maxAuthorChatNumber):
            maxAuthorChatNumber = userChatCount[author['id']]
            maxAuthorData = author

        # If you want to isolate out a user
        if(authID=='UC9_dMgvP46Jbt5WF1dYvZPg'):
            print(msg['message'])



    msgType = msg['message_type']
    if(msgType not in seenMessageTypes):
        # print("%s added to seenMessageTypes" % (msgType))
        # Having the add under the check is redundant but we need it anyway for the print
        seenMessageTypes.add(msgType)


    # if(idx==500):
    #     break

print("Seen message types:")
print(seenMessageTypes)

print("")

print("Biggest chatter: %s" % (maxAuthorData['name']))
print(maxAuthorData)
print("Number of chats: %d" % (maxAuthorChatNumber))

chatLogJSONFile.close()