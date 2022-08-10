Getting Started
===================================

Welcome to the getting started guide for Chat Analyzer! In this guide, 
we'll cover the basics of how to use the software, some intermediate and advanced uses, 
and overall best practices when using the software.

.. warning:: 

    This guide, the software itself, and the website visualization are still in the beta phase of development and not yet complete.
    Because Twitch Rivals started recently, I decided to make the software availiable because I believe it will
    be useful to some people even in its current state. If there are any questions/concerns, feel free to contact me at info@chatanalyze.com, or
    shoot me a DM on discord ``NaCl-y#1117``.

.. note:: 
    
    Even though this guide is not yet complete, the available arguments/flags are fully documented by running the ``-help`` flag,
    and can also be found on the :doc:`Command Line Interface Specification page </cli>`.

Basic Usage
------------

In this section, we'll cover the basic steps necessary to use the Chat Analyzer software.


Step 1 - Installation
***********************************

If you haven't already installed the software, you can easily install the software one of two ways:

This tool is distributed on PyPI_ and can be installed with pip_:

.. _PyPI: https://pypi.org/project/chat-downloader/
.. _pip: https://pip.pypa.io/en/stable/

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


Step 2 - Pick a Past Stream
*****************************

By default, we will be downloading the chatlog data to analyze from a past stream's url.
Currently we support Twitch and YouTube streams/VODs. For a Twitch stream, simply copy the ``twitch.tv...`` link
to use with the analyzer. For a YouTube stream, it is best to use the "share" button underneath 
the video player to get the ``youtu.be`` link, but the analyzer itself will still work with a 
standard YouTube link.

For example, a youtube/twitch link might look like:

.. code-block:: shell
    
    https://youtu.be/d6JXhg1GBKs
    https://www.twitch.tv/videos/1552248469


For help picking the right type of link, you can reference the rules & criteria under the url_ section.


Step 3 - Run the Chat Analyzer
********************************

Now that we have the link, all we have to do is run the analyzer and give it the link as an input. Open up a terminal/command prompt and run the following command:

.. code-block:: shell

    chat_analyzer '<link>'

The program will produce an output file in the directory that the program was run in (the current directory). The output file/filepath can also be assigned
using the ``-o`` flag:

.. code-block:: shell

    chat_analyzer '<link>' -o '<output_filepath>'

After starting the program, the chatlog download will initiate and you should see output that looks something like this:

.. code-block:: shell

    Getting chatlog using Xenonvas chat-downloader (https://github.com/xenova/chat-downloader)...
    Successfully retrieved chat generator:
        Title: <video_title>
        Duration: ... (... seconds)
    NOTICE: Downloading chats from a url is the largest rate-limiting factor.
                If you intend to sample the data differently multiple times, consider using chatfile mode, or saving the chat data with --save-chatfile.

    Processing (Sampling) chat data...
      Completion   |   Processed Media Time    |   Messages Processed
        (...%)     |         ... / ...         |         ...        
    
As messages are downloaded, you will see constant updates indicating the progress of the download.    

.. note:: 
    The downloading of chat data is the slowest part of the entire process. Twitch/YouTube limits the rate at which chat data can be downloaded. If you want to resample
    the chat multiple times, look into using chatfile_ mode

After the download has finished, you should see the following report:

.. code-block:: shell

    Downloaded & Processed ... messages.
    Post-processing (Analyzing)...
    Post-processing (Analyzing) complete!
    Successfully wrote chat analytics to `<output_filepath>`

The analyzed output file can now be found at ``<output_filepath>``!

Step 4 - Visualize the Chat Data
**********************************

Now that we have generated the output file, we will use the visualizer found at `chatanalyze.com/visualize`_ to nicely
visualize the analytical data. Once on the page, all you have to do is select the output file and the visualization data will
automatically appear on screen. 

.. _chatanalyze.com/visualize: https://chatanalyze.com/visualize

The two core features currently availiable are the **graph** representation of chat activity, and the **highlights** table. The graph
provides a quick visual reference to the chat activity at any given point throughout the whole stream. The highlights table provides a useful way
of examining the highest-activity portions of the video, and quickly jumping to those sections of the stream using the "Jump To" functionality.


Usage Modes & Source
---------------------

In its simplest form, this software outputs information about a chatlog associated with a livestream.
Regardless of the mode that is used, the output file format is the same (More details under :doc:`Output Specification </output>`).

The three modes that can be used all refer to the type of input the program receieves.

.. When re-process is supported,  detail, add a pros/cons to using each strategy.
..     C-download then our software separately:
..       - Pros: Run very different analysis styles on the raw data quickly without having to re-download
..       - Cons: Raw data takes up a bunch of space, and is not necessary for all use cases
..     Integrated C-download (recommended & default):
..       - Pros: Only store what you need on your machine
..       - Cons: Can only re-post-process for spikes and other data, but sample size is fixed without a re-download


url
**********

The default mode, ``url`` accepts a link from a supported streaming site,
downloads the raw chat data, processes the raw chat data into samples, and analyzes the samples.

Streaming services like Twitch & YouTube limit the rate at which we can download chat messages, 
The slowest part of the analytics process is downloading the chats themselves.

The link provided **must**: 

- Be a link to a past (finished) livestream.
- Come from a supported streaming site.
- Be the original video with the chatlog/replay. (It can't be a reposted video.)

.. note::

    If you want to analyze a YouTube stream, it is recommended
    you provide the ``youtu.be`` link generated through the "share"
    feature of the video.

    .. image:: ./YoutubeShare.png
        :width: 100
        :alt: Youtube Share Button found beneath YouTube videos
        :align: center

    While the standard YouTube video link will work to download the chat and produce the data, 
    the ``youtu.be`` short link works better with the visualizer at `chatanalyze.com`_, 
    enabling "Jump to" functionality (quickly jumping to highlighted points in the video).

.. _chatanalyze.com: https://chatanalyze.com/


chatfile
**********

``chatfile`` mode ...

Note that ... for visualization....

If you want to re-enable, you can go into the JSON file and manually replace/paste the link to the URL 
in the mediaSource field, which will re-enable functionality ...


internally we use xenovas makign comaptability easy...

the chatfile mode can be activated using the ``--mode chatfile`` command line argument.

reanalyze
**********

``reanalyze`` mode ...



.. .. code:: console

..     TODO: Discuss modes:
..     url:...
..     chatfile: JSON from Xenova\'s chat-downloader to JSON analytic data to be used for visualization (or -sc)
..     reanalyze:...



Examples
--------

TODO: add...

.. This will eventually describe a standard user flow, when to reanalyze, when to url, when its good to save chatfile, etc...

.. For now, just reference :doc:`Command Line Interface </cli>`

.. visualizer will have better results for youtube if you use the share link thats youtu.be

.. (remember to update the link in the README.rst if we remove cli and replace it with getting started...)