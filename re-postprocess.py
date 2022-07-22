"""Run this on a given output file in order to re-run the chatlog post-process given a diff set of parameters.

Mainly used for testing purposes. Especially helpful when testing spike-detection algos
"""

import numpy as np

import json
import dataformat


testFile1 = 'output/XQC_MEGADRAMA.json'
testFile2 = 'output/3 Peens Charity Stream.json'

fileToUse = testFile1

def percentile_test(fieldToUse, samples):

    desired_percentiles = [0, 25, 50, 75, 90, 100]
    fieldValues = [s[f"{fieldToUse}"] for s in samples]
    percentile_values = np.percentile(fieldValues, desired_percentiles)
    print("\033[32;1m")
    print(f"{fieldToUse} percentiles: \033[0m\n[0, 25, 50, 75, 90, 100]")
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


#main function
def main():

    jsonData = None

    # gets one of the json output files from the chat-analyzer.py script
    with open(fileToUse, 'r') as f:
        jsonData = json.load(f)

    # print(jsonData['samples'])
    samples = jsonData['samples']

    percentile_test("avgActivityPerSecond", samples)
    median("avgActivityPerSecond", samples)
    mean("avgActivityPerSecond", samples)
    stdDeviation("avgActivityPerSecond", samples, jsonData=jsonData)
    

    
    
    
    





main()