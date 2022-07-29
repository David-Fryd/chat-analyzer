# chat-analyzer
JSON from Xenova's chat-downloader to JSON analytic data to be used for visualization

```
// Mockup JSON Data
{
  "platform" : "youtube",  // youtube & twitch are currently supported (inform what data/fields the JSON contains)
  "timeInterval" : 5,      // Time interval in seconds (how granular the analytics are)
  
   "rawData" : [           // Array where each element represents a time interval     
    {"timeStamp" : 0, "intervalActivity" : 10, "chatMessages" : 8, "superChats" : 0, "newMembers" : 2, . . .}, // if interval==5, this is 0:00 - 0:05
    {"timeStamp" : 5, "intervalActivity" : 8, "chatMessages" : 8, "superChats" : 0, "newMembers" : 0, . . .},  // if interval==5, this is 0:05 - 0:10
    . . .                                                                                                      // etc...
    {"timeStamp" : 1650, "intervalActivity" : 50, "chatMessages" : 48, "superChats" : 1, "newMembers" : 1, . . .}, 
    {"timeStamp" : 1655, "intervalActivity" : 46, "chatMessages" : 46, "superChats" : 0, "newMembers" : 0, . . .},
    . . .
    {"timeStamp" : 2700, "intervalActivity" : 45, "chatMessages" : 41, "superChats" : 0, "newMembers" : 4, . . .},
  ],
  
  "videoLength" : 2702,    // In seconds 
  
  "totalActivity" : 2304,  // Total # of any type of message
  "averageActivity" : 15,  // Average intervalActivity
  
  "totalChatMessages" : 2112,
  "averageChatActivity" : 15,
  
  . . . (total/Avg superchats, newMembers, etc... (need to check YT/Twitch/Xenova docs to see what possible message types we can track are))
  . . . (total/Average of each datapoint)
  
  "maxIntervalActivity" : {"timeStamp" : 1650, "intervalActivity" : 50, "chatMessages" : 48, "superChats" : 1, "newMembers" : 1, . . .}, 
  // Note: I imagine this will usually be toward the start of a video but I could be wrong
  "minIntervalActivity" : {"timeStamp" : 5, "intervalActivity" : 8, "chatMessages" : 8, "superChats" : 0, "newMembers" : 0, . . .},
  
  
  // Need to report/distinguish long sustained activity levels as well as peak activity
  ("listOfMaxIntervals : [..., ..., ...]")
  ("listOfMinIntervals : [..., ..., ...]")
  ("longestSustainedActivity" : {}) // is this arbitrary? highest "1 min period" do we keep track of highest 1,5,10 min periods?
  
  
  (
  use statistics in a 2-pass fashion to rule out outliers? or at least recognize and report outliers i.e:
  maxIncludingOutliers: ...
  maxOutliersEliminated: ...
  )
  
  
  // User specific data too
  
  "uniqueChatters" : 1460
  
  // Tracks the [specified number] chatters with the most messages
  "mostChatted" : [
    {"numChats" : 120, "author" : {. . .(verbatim author info from the chat-downloader) }}
  
  ]
  
  

}



//NOTE: JSON DATA WILL LOOK DIFFERENT DEPENDING ON STREAMING SERVICE BECAUSE WE KEEP TRACK OF DIFFERENT THINGS BASED ON THE SERVICE
```
