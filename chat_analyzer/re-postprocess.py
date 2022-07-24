"""Run this on a given output file in order to re-run the chatlog post-process given a diff set of parameters.

Mainly used for testing purposes. Especially helpful when testing spike-detection algos
"""

import numpy as np

import json
from dataformat import YoutubeChatAnalytics, TwitchChatAnalytics, YOUTUBE_NETLOC, TWITCH_NETLOC 


# Twitch
testFileA = 'output/XQC_MEGADRAMA.json'
testfileD = 'output/The 1000 Push-Up Stream....json'

# Youtube
testFileB = 'output/3 Peens Charity Stream.json'
testFileC = 'output/LUDWIG\'S MILLION DOLLAR GAME ft. @MrBeast @xQcOW @Ninja @Phil Hellmuth #POSITIVITY.json'


testFiles = [testFileA, testFileB, testFileC, testfileD]

def percentile_test(fieldToUse, samples):


    desired_percentiles = [0, 25, 50, 75, 90, 95, 99, 100]
    fieldValues = [s[f"{fieldToUse}"] for s in samples]
    percentile_values = np.percentile(fieldValues, desired_percentiles)
    print("\033[32;1m", end="")
    print(f"{fieldToUse} percentiles: \033[0m\n{desired_percentiles}")
    print(percentile_values)
    print("Total number of samples: " + str(len(samples)))
    for idx,percentile in enumerate(percentile_values):
        remainingSamples = [s for s in samples if s[f"{fieldToUse}"] >= percentile]
        print(f"# samples >= {percentile} ({desired_percentiles[idx]}%): {len(remainingSamples)}")

def median(fieldToUse, samples):
    fieldValues = [s[f"{fieldToUse}"] for s in samples]
    median = np.median(fieldValues)
    print(f"\033[33;1m{fieldToUse} median: {median}\033[0m")
    return median

def mean(fieldToUse, samples):
    fieldValues = [s[f"{fieldToUse}"] for s in samples]
    mean = np.mean(fieldValues)
    print(f"\033[35;1m{fieldToUse} mean: {mean}\033[0m")
    return mean

def stdDeviation(fieldToUse, samples, jsonData):

    print(f"overallAvgActivityPerSecond: {jsonData['overallAvgActivityPerSecond']}")

    fieldValues = [s[f"{fieldToUse}"] for s in samples]
    stdDev = np.std(fieldValues)
    print(f"\033[34;1m{fieldToUse} stdDev: {stdDev}\033[0m")
    return stdDev

# TODO: Custom find_spikes function here to test

#main function
def main():

    jsonData = None

    for file in testFiles:
        print()
        print(f"\033[31;4m{file}\033[0m")
        # gets one of the json output files from the chat-analyzer.py script
        with open(file, 'r') as f:
            jsonData = json.load(f)

        # print(jsonData['samples'])
        j = jsonData

        # TODO: Have to manually set fields and create empty objects, because this mapping method is not suitable
        # for nested classes (inside of the CA class we have list of spikes, samples, etc.)

        # Basically, need to implement a full JSON file to object mapping here. This is a feature for later down the road,
        # worth implementing because of time savings with re-analyzation. For now focus on main features...

        if(jsonData['platform']== YOUTUBE_NETLOC):
            ca = YoutubeChatAnalytics(**j)
        elif(jsonData['platform']== TWITCH_NETLOC):
            ca = TwitchChatAnalytics(**j)

        # ca = ChatAnalytics(**j)

        print(ca.platform)







        # percentile_test("avgActivityPerSecond", samples)
        # median("avgActivityPerSecond", samples)
        # mean("avgActivityPerSecond", samples)
        # stdDeviation("avgActivityPerSecond", samples, jsonData=jsonData)

        # if(jsonData['platform']==dataformat.YOUTUBE_NETLOC):
        #     percentile_test("superchats", samples)
        #     median("superchats", samples)
        #     mean("superchats", samples)
        #     stdDeviation("superchats", samples, jsonData=jsonData)

        #     percentile_test("memberships", samples)
        #     median("memberships", samples)
        #     mean("memberships", samples)
        #     stdDeviation("memberships", samples, jsonData=jsonData)


        # # TODO/NOTE: Doesnt really make sense to do percentile stuff for stuff that doesnt happen frequently. Instead shift focus to avg/median chats per user
        # if(jsonData['platform']==dataformat.TWITCH_NETLOC):
        #     # perform the sequence on subscriptions
        #     percentile_test("subscriptions", samples)
        #     median("subscriptions", samples)
        #     mean("subscriptions", samples)
        #     stdDeviation("subscriptions", samples, jsonData=jsonData)

        #     # do the same for giftSubscriptions and upgradeSubscriptions
        #     percentile_test("giftSubscriptions", samples)
        #     median("giftSubscriptions", samples)
        #     mean("giftSubscriptions", samples)
        #     stdDeviation("giftSubscriptions", samples, jsonData=jsonData)

        #     percentile_test("upgradeSubscriptions", samples)
        #     median("upgradeSubscriptions", samples)
        #     mean("upgradeSubscriptions", samples)
        #     stdDeviation("upgradeSubscriptions", samples, jsonData=jsonData)


        # TODO: Allow input of how many seconds of highlighted video, and it will find an appropriate percentile which reflects only the top x minutes of video
        # Basically, sort the list and take the top x/interval samples? (need to group samples that are next to eachother together, because chronology is destroyed with this method)
    

    
    
    
    





main()