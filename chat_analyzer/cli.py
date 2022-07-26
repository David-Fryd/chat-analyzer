import argparse

from metadata import (
    __version__,
    __summary__,
    __program__
)

from analyzer import run, MAX_INTERVAL, MIN_INTERVAL
from dataformat import SUPPORTED_PLATFORMS

def check_interval(interval):
    """
    Based on the MAX_INTERVAL and MIN_INTERVAL from chat_analyzer.py,
    ensure that the entered interval respects that boundary"""
    interval = int(interval)
    if interval < MIN_INTERVAL:
        raise argparse.ArgumentTypeError(f"Interval must be at least {MIN_INTERVAL} and at most {MAX_INTERVAL}")
    if interval > MAX_INTERVAL:
        raise argparse.ArgumentTypeError(f"Interval must be at most {MAX_INTERVAL} and at least {MIN_INTERVAL}")
    return interval

def check_positive_int(value):
    """
    Check that the value is a positive integer"""
    value = int(value)
    if value < 0:
        raise argparse.ArgumentTypeError("Value must be a positive integer")
    return value

def main():
    parser = argparse.ArgumentParser(description=__summary__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Parser info
    parser.prog = __program__
    parser._positionals.title = 'Required Arguments'
    parser._optionals.title = 'Optional Arguments'
    # parser._subparsers.title = 'Subcommands'

    # Meta-arguments
    parser.add_argument('--version', action='version', version=__version__)

    # TODO: Add subparser for different modes (instead of having a --modes thing)?
    # https://stackoverflow.com/questions/8250010/argparse-identify-which-subparser-was-used/9286586#9286586
    # https://stackoverflow.com/questions/17073688/how-to-use-argparse-subparsers-correctly
    # TODO: Add mutually exclusive 'MODE
        # standard has everything built in
        # re-process an old output file
        # process a downloaded chat json file produced separately by the chat-downloader

    # Required arguments
    parser.add_argument("source", type=str,\
        help=f"""A url to a past stream/VOD. We currently only support links from: {', '.join(SUPPORTED_PLATFORMS)}.
        In --mode=='chatfile' or 'reprocess', source is a filepath to a 
        .json raw chat log produced by Xenonva's chat-downloader, 
        or a .json output file previously produced by this program (respectively).""")

    # Sampling Arguments
    sampling = parser.add_argument_group("Sampling")
    sampling.add_argument("--interval", "-i" , default=5, type=check_interval, help="""
            The time interval (in seconds) at which to compress datapoints into samples. i.e. Duration of the samples. The smaller the interval, the more 
            granular the analytics are. At interval=10, each sample's fields contain data about 10 seconds of cumulative data.
            *(With the exception of the last sample, which may be shorter than the interval.)*""")
    sampling.add_argument("--print-interval", default=100, type=int, help="Number of messages between progress updates to the console. If <= 0, progress is not printed.")



    # 
    mg = parser.add_argument_group("Program Behavior (Mode)")
    mode_group = mg.add_mutually_exclusive_group()
    mode_group.add_argument("--mode", default="url", choices=["url", "chatfile", "reprocess"], type=str,\
        help="""The program can be run in three modes:
        \033[1m\'url\'\033[0m mode (default) will download the chatlog and simultaneously process the chats as they are downloaded.
        \033[1m\'chatfile\'\033[0m mode reads from a .json file with raw chat data produced by Xenonva's chat-downloader.
        \033[1m\'reprocess\'\033[0m mode reads from a .json file produced by this program in a previous run, and recalculates the post-processed data based on the existing samples.""")
    
    
    



    # TODO: Settings for finding spike. Sensitivity based, or "top-5 based" or...?

    # TODO: Add a console output group (verbose, quiet, progress update, etc...)
    

    # output_group = parser.add_argument_group("Output")
    

    debug = parser.add_argument_group('Debugging')
    debug.add_argument('--debug','-d', action='store_true', help='Enable debug mode (debug info is printed)')
    debug.add_argument('--break','-v', type=check_positive_int, help='Stop execution after processing this number of messages. WARNING: May cause undefined behavior, because certain parts of execution assume that chatlog has been completely processed.')

    args = parser.parse_args()

    run(**args.__dict__)




# Some testing URLs
# TODO: Replace url with argparse arg
# url = 'https://www.youtube.com/watch?v=97w16cYskVI' # yt stream that comes with lots of message types (retrieved from chat-downloader testing sample) TODO: [blocked now?! check into]
# url = 'asdds.com/a/b/c/d' # (error) invalid URL
# url = 'https://www.youtube.com/watch?v=5qap5aO4i9A' # (error) stream still live (lo-fi hip hop girl runs 24/7)
# url = 'https://www.twitch.tv/videos/1522574868'  # summit1g's 14 hour stream
# url = 'https://www.youtube.com/watch?v=PTWpoZITraE&ab_channel=RobScallon' # (error) Youtube video without chat replay
# url = 'https://www.youtube.com/watch?v=UR902_1LhVk&t=24333s&ab_channel=Ludwig' # Ludwig's 1 million dollar game poker stream, 8:57:25, 158366 totalActivity
# # url = 'https://www.youtube.com/watch?v=vjBNozL9Daw' #(error for now TODO: test later) no chat replay
# url = 'https://www.twitch.tv/videos/1289325547' # markiplier peen stream
# url = 'https://www.twitch.tv/videos/1530042943' # MMG's stream
# url = 'https://clips.twitch.tv/AverageSparklyTortoisePeoplesChamp' # (error) chat replay not avail
# url = 'https://www.twitch.tv/videos/1534993737' # Huge fkin XQC stream

# TODO: Check the one below for type: sponsorships_gift_redemption_announcement
# TODO: Look into sponsorships_gift_redemption_announcement (...'was gifted a membership by...')
# url = 'https://www.youtube.com/watch?v=1jRVuFcBj3M&list=PLLGT0cEMIAzcd5XagsMwz22-NFPmToKIP&index=2&ab_channel=Ludwig'

# TODO: Consider 'raid' type:
# url = 'https://www.twitch.tv/videos/1538666427'


# python chat_analyzer 'https://www.twitch.tv/videos/1522574868' --print-interval 100 -i 5