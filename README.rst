***************
Chat Analyzer
***************

`Chat Analyzer`_ is a tool used to process and analyze chat data 
from past live streams, then reports useful information about chat activity over the stream's lifetime. 

.. _Chat Analyzer: https://github.com/David-Fryd/chat-analyzer

.. role:: red

An example of using :red:`interpreted text`

It enables **editors**

############
Installation
############

todo...

#####
Usage
#####

Command line
------------

.. code:: console

    usage: chat_analyzer [-h] [--version] [--platform {youtube,twitch}]
                        [--mode {url,chatfile,reanalyze}]
                        [--save-chatfile-output SAVE_CHATFILE_OUTPUT]
                        [--interval INTERVAL] [--print-interval PRINT_INTERVAL]
                        [--highlight-percentile HIGHLIGHT_PERCENTILE]
                        [--highlight-metric {usersPSec,chatsPSec,activityPSec}]
                        [--description DESCRIPTION] [--output OUTPUT] [--nojson]
                        [--debug] [--break BREAK]
                        source

    A program that processes and analyzes chat data from a past live stream, then
    reports useful information about chat activity over the stream's lifetime.


Some console code: 

.. code:: console

    beep 123


Front end advertising:
  For creators: don't forget to subscribe effective? what is most engaging part of stream?

  For editors: more quickyl find interesting parts

  potential creators:
      pick popular youtube/twitch streamers, see what part of their streams generate the most engagement

  Researchers


##############
Special Thanks
##############

This project wouldn't exist without `Xenova and his chat-downloader`_! 
All of the platform-standardization and downloading logic that he worked on for his downloader also made the analyzer
infinitely more easy to write. If you are willing, go on over to his repo and show him some support as well :)

.. _Xenova and his chat-downloader: https://github.com/xenova/chat-downloader