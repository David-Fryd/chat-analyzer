***************
Chat Analyzer
***************

.. image:: https://badge.fury.io/py/chat-analyzer.svg
    :target: https://badge.fury.io/py/chat-analyzer
    :alt: PyPI version

.. https://badge.fury.io/for/py/chat-analyzer

.. image:: https://img.shields.io/pypi/status/chat-analyzer.svg
    :target: https://pypi.python.org/pypi/chat-analyzer/
    :alt: PyPI status
   
.. image:: https://readthedocs.org/projects/chat-analyzer/badge/?version=latest
    :target: https://chat-analyzer.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

`Chat Analyzer`_ is a tool used to process and analyze chat data 
from past live streams, providing summarized information about chat activity over the stream's lifetime. 
The information currently reported primarily revolves around the activity per second for various metrics,
with future plans to incorporate semantic analysis into the program. (*See the* `Output`_ *section for output specification*)

.. _Chat Analyzer: https://github.com/David-Fryd/chat-analyzer

Paired with the visualizer hosted on `chatanalyze.com`_, easily understand and interpret
how your chat responds to your performance!

.. _chatanalyze.com: https://chatanalyze.com/

*Currently both YouTube and Twitch VODs are supported.*

#################
Target Auidence: 
#################

Anyone can use this tool on anyone's streams, enabling people beyond the creators themselves to view and use chat analytics data.

- Editors 
    
  - Need to edit down an 18 hour stream into a 20 minute youtube video? Quickly find
    parts of the stream where chat went crazy and look there first! Chat activity is 
    generally a great proxy for how exciting/engaging the stream is at any moment in time. Not only
    will you more quickly find the most interesting sections of the stream, but you'll
    ensure that you don't miss any moments that you might have might have slept through during your 18 hour-long
    editing session.
  - Are you a creator that edits your own videos? Focus more on creating the content you love, and less on the tedious
    work of editing.
  
- Streamers / Creators
  
  - Draw specific connections between the content you make and how it engages your community. What type of content makes
    your chat go wild? What strategies/types of content are more effective than others?
  - See the exact moments people decide to subscribe/become members- what type of content moves people so much that
    they decide to support you and your stream?

..   - helping you understand what you say/do that makes
..     people
  
..   - Connect your content to your chat. Which content
..   - Better understanding...
..   - What parts of
..   - Learn...
..   - For creators: don't forget to subscribe effective? what is most engaging part of stream?
..   - Take burden off editors. Because your editors will have access to the chat analytics data, there is less
..     of a need to manually mark sections of your own video... of course its a backup but still less work...?

- Small/Upcoming streamers
  
  - Immitation is the best form of flattery. Pick a popular streamer and see what parts of their stream generate the most engagement!
    What type of content/strategies can you use to make your stream more engaging?

.. - Developers
  
..   - Making an app comparing streamers based on chat activity? 



############
Installation
############

This tool is distributed on PyPI_ and can be installed with ``pip``:

.. _PyPI: https://pypi.org/project/chat-downloader/

.. code:: console

    pip install chat-analyzer

To update to the latest version, run: 

.. code:: console

    pip install chat-analyzer --upgrade


Alternatively, the tool can be installed with ``git``:

.. code:: console

    git clone https://github.com/David-Fryd/chat-analyzer.git
    cd chat-analyzer
    python setup.py install

#####
Usage
#####

This section is next on the to-do list!

A deeper dive into the usage can be found on the `Getting Started <https://chat-analyzer.readthedocs.io/en/latest/gettingstarted.html>`_ page.

.. code:: console

    TODO: Discuss modes:
    url:...
    chatfile: JSON from Xenova\'s chat-downloader to JSON analytic data to be used for visualization (or -sc)
    reanalyze:...

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


More complete documentation can be found on the `Command Line Usage <https://chat-analyzer.readthedocs.io/en/latest/cli.html>`_ page.


######
Output
######

For non-developers, I highly recommend you use the visualizer on `chatanalyze.com`_ to view the output of the program.
Simply follow the instructions and upload the output json file to the visualizer. 

All of the analytical data is output in a single ``.json`` file. Certain datapoints exist regardless of the platform
the VOD is from, some datapoints are specific to the platform.

More complete documentation can be found on the `Output Specifications <https://chat-analyzer.readthedocs.io/en/latest/output.html>`_ page.



##############
Special Thanks
##############

This project wouldn't exist without `Xenova and their chat-downloader`_! 
All of the platform-standardization and downloading logic that they worked on for their downloader made the analyzer
infinitely easier to write. In order to avoid compatability issues, this software comes packaged with a frozen version
of the downloader src, and all credit goes to Xenova for the contents in the ``chat_downloader`` directory. Since this
was also my first ever python project made for distribution, their organizational structure and style was
invalueable reference for the packaging/distribution process. If you are willing, go on over to their repo and show them some support as well :)

.. _Xenova and their chat-downloader: https://github.com/xenova/chat-downloader