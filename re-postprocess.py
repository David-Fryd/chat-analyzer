"""Run this on a given output file in order to re-run the chatlog post-process given a diff set of parameters.

Mainly used for testing purposes. Especially helpful when testing spike-detection algos
"""

import numpy as np

import json
import dataformat


testFile1 = 'output/XQC_MEGADRAMA.json'
testFile2 = 'output/3 Peens Charity Stream.json'

fileToUse = testFile2

#main function
def main():

    jsonData = None

    # gets one of the json output files from the chat-analyzer.py script
    with open(fileToUse, 'r') as f:
        jsonData = json.load(f)

    # print(jsonData['samples'])
    samples = jsonData['samples']
    
    desired_percentiles = [0, 25, 50, 75, 90, 100]
    activityPerSecond = [s["avgActivityPerSecond"] for s in samples]
    percentile_activityPerSecond = np.percentile(activityPerSecond, desired_percentiles)
    print("")
    print("activityPerSecond percentiles: \n[0, 25, 50, 75, 90, 100]")
    print(percentile_activityPerSecond)
    print("")
    print("Total number of samples: " + str(len(samples)))
    for percentile in percentile_activityPerSecond:
        remainingSamples = [s for s in samples if s["avgActivityPerSecond"] >= percentile]
        print(f"# samples >= {percentile}: {len(remainingSamples)}")
    
    





main()