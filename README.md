# chat-analyzer
JSON from Xenova's chat-downloader to JSON analytic data to be used for visualization

```
// Mockup JSON Data
{
  "platform" : "youtube",  // youtube & twitch are currently supported (inform how the JSON is structured
  "videoLength" : 153,     // In seconds 
  "timeInterval" : 5,      // Time interval in seconds (how granular the analytics are)
  
  "totalActivity" : 2304,  // Total # of any type of message
  "averageActivity" : 15,  // Average intervalActivity
  
  "totalChatMessages" : 2112,
  "averageChatActivity" : 15,
  
  
  // The below fields are platform dependent... youtube might look like:
  
  // total/Avg superchats, newMembers, etc... (need to check YT/Twitch/Xenova docs to see what possible message types we can track are)
  
  
  "rawData" : [            // Array where each element represents a time interval
    {"intervalActivity" : 10, "chatMessages" : 8, "superChats" : 0, "newMembers" : 2, . . .}, // if interval==5, this is 0:00 - 0:05
    {"intervalActivity" : 10, "chatMessages" : 8, "superChats" : 0, "newMembers" : 2, . . .}, // if interval==5, this is 0:05 - 0:10
    {"intervalActivity" : 10, "chatMessages" : 8, "superChats" : 0, "newMembers" : 2, . . .}, // etc...
    {"intervalActivity" : 10, "chatMessages" : 8, "superChats" : 0, "newMembers" : 2, . . .},
    . . .
    {"intervalActivity" : 10, "chatMessages" : 8, "superChats" : 0, "newMembers" : 2, . . .},
  ]
}



//NOTE: JSON DATA WILL LOOK DIFFERENT DEPENDING ON STREAMING SERVICE BECAUSE WE KEEP TRACK OF DIFFERENT THINGS BASED ON THE SERVICE
```
