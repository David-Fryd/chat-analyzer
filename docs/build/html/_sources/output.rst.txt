Chat Analyzer Output Specifications
===================================

All of the analytical data is output in a single .json file. Certain datapoints exist regardless of the platform the VOD is from, some datapoints are specific to the platform.

**Common fields among ALL platfroms**: 
______________________________________

.. TODO: Can we somehow hook up the autodocs to this?

.. autoclass:: chat_analyzer.dataformat.ChatAnalytics
    :members:
    :undoc-members:
    :show-inheritance:


Example JSON output:

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