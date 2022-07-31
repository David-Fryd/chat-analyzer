Output Specifications
===================================

All of the analytical data is output in a single .json file. Certain datapoints exist regardless of the platform the VOD is from, some datapoints are specific to the platform.

**Common fields**: 
########################################

Chat Analytics Data
----------------------------------------

The Chat Analytics object is directly transformed into JSON data.

.. autoclass:: chat_analyzer.dataformat.ChatAnalytics
    :members:
    :show-inheritance:

Sample Data
----------------------------------------

The main JSON data contains a ``sample`` field comprised of a list of Sample objects.

.. autoclass:: chat_analyzer.dataformat.Sample
    :members:
    :show-inheritance:

Highlight Data
----------------------------------------

The main JSON data contains a ``highlights`` field comprised of a lsit of Highlight objects.
Currently, there are no platform-specific fields corresponding to Highlights (i.e. highlight
objects look the same for all platforms).

.. autoclass:: chat_analyzer.dataformat.Highlight
    :members:
    :show-inheritance:





**Twitch-specific fields**: 
########################################

Chat Analytics Data (Twitch)
----------------------------------------

.. autoclass:: chat_analyzer.dataformat.TwitchChatAnalytics
    :members:
    :show-inheritance:

Sample Data (Twitch)
----------------------------------------

.. autoclass:: chat_analyzer.dataformat.TwitchSample
    :members:
    :show-inheritance:



**YouTube-specific fields**: 
########################################

Chat Analytics Data (YouTube)
----------------------------------------

.. autoclass:: chat_analyzer.dataformat.YoutubeChatAnalytics
    :members:
    :show-inheritance:

Sample Data (YouTube)
----------------------------------------

.. autoclass:: chat_analyzer.dataformat.YoutubeChatAnalytics
    :members:
    :show-inheritance:

.. .. automodule:: chat_analyzer.dataformat
..     :members:
..     :show-inheritance:
    

    .. :undoc-members:


Example JSON output:
########################################

An output JSON file might look something like...
(*Note, only generic fields are shown. Platform-specific fields would be included in
their respective sections, the main analytics data in the main body of the JSON, and the
sample data within each sample.*)

.. code-block::

    {
        "duration": 7386.016,
        "interval": 5,
        "description": "description ",
        "program_version": "1.0.0b5",
        "platform": "www.....com",
        "duration_text": "2:03:06",
        "interval_text": "0:05",
        "mediaTitle": "The title of the VOD",
        "mediaSource": "https://www...",
        "samples": [
            {
            "startTime": 0,
            "endTime": 5,
            "sampleDuration": 5,
            "startTime_text": "0:00",
            "endTime_text": "0:05",
            "activity": 10,
            "chatMessages": 9,
            "firstTimeChatters": 9,
            "uniqueUsers": 9,
            "avgActivityPerSecond": 2.0,
            "avgChatMessagesPerSecond": 1.8,
            "avgUniqueUsersPerSecond": 1.8,
            "_userChats": {},
            },
            ...
        ],
        "totalActivity": 42547,
        "totalChatMessages": 42034,
        "totalUniqueUsers": 12533,
        "overallAvgActivityPerSecond": 5.760480345561126,
        "overallAvgChatMessagesPerSecond": 5.691024768968819,
        "overallAvgUniqueUsersPerSecond": 5.66955345060893,
        "highlights": [
            {
            "startTime": 4405,
            "endTime": 4420,
            "description": "avgUniqueUsersPerSecond sustained at or above [8.6]",
            "type": "avgUniqueUsersPerSecond",
            "peak": 11.2,
            "avg": 9.866666666666665,
            "duration": 15,
            "duration_text": "0:15",
            "startTime_text": "1:13:25",
            "endTime_text": "1:13:40"
            },
            ...
        ],
        "highlights_duration": 540,
        "highlights_duration_text": "9:00",
        "spikes": [],
        "_overallUserChats": {},
        "_currentSample": null,
    }