import argparse

from .metadata import (
    __version__,
    __summary__,
    __program__
)

from .analyzer import run, MAX_INTERVAL, MIN_INTERVAL
from .dataformat import SUPPORTED_PLATFORMS, SUPPORTED_PLATFORMS_SHORTHANDS

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

def check_percentile_float(value):
    """
    Check that the value is between 0 and 100 exclusive"""
    value = float(value)
    if value <= 0 or value >= 100:
        raise argparse.ArgumentTypeError("Percentile must be between 0 and 100 exclusive")
    return value


# Anecdotally determined
# For messages that wrap w/ R|, this helps keep spacing consistent. No good way to access indent from argparser
# INDENT_INCREMENT = 2
# Standard help position is 2*INDENT_INCREMENT according to the argparse src
HELP_INDENT_POSITION = 3

# Constants for the argparse get help string
# SUPPRESS = '==SUPPRESS=='
# ZERO_OR_MORE = '*'
# OPTIONAL = '?'
class SmartFormatter(argparse.ArgumentDefaultsHelpFormatter):
    """
    Any help string starting with 'R|' has its newlines (\n) preserved, in addition to
    keeping the fxnality from the HelpFormatter (displaying defaults next to descriptions).
    
    Adapted from and thanks to:
    https://stackoverflow.com/questions/3853722/how-to-insert-newlines-on-argparse-help-text
    """

    # def __init__(self) :
    #     super().__init__(indent_increment=INDENT_INCREMENT)

    def _split_lines(self, text, width):
        if text.startswith('R|'):
            lineList = text[2:].splitlines() 
            # Remove whitespace from before each of the strings so nice spacing doens't affect output inset
            lineList = [line.lstrip() for line in lineList]
            # NOTE: Not using textwrap.wrap here like in argparse because it messes w escape characters. Anecdotally determined indent position instead:
            import textwrap
            lineList = [str(textwrap.fill(line, width, subsequent_indent="\t"*HELP_INDENT_POSITION)) for line in lineList]
            return lineList
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)
    
    # def _get_help_string(self, action):
    #     help = action.help
    #     print("before key error?")
    #     if '%(default)' not in action.help:
    #         print("after key error?")
    #         if action.default is not SUPPRESS:
    #             defaulting_nargs = [OPTIONAL, ZERO_OR_MORE]
    #             if action.option_strings or action.nargs in defaulting_nargs:
    #                 help += ' \033[1m(DEFAULT: %(default)s)\033[0m'
    #     return help

def main():
    parser = argparse.ArgumentParser(description=__summary__, formatter_class=SmartFormatter)

    # Parser info
    parser.prog = __program__
    parser._positionals.title = 'Required Arguments'
    parser._optionals.title = 'Optional Arguments'
    # parser._subparsers.title = 'Subcommands'

    # Meta-arguments
    parser.add_argument('--version', action='version', version=__version__)

    # Required arguments
    parser.add_argument("source", type=str,\
        help=f"""R|
        Raw chat data to process and analyze, or processed sample data to re-analyze.

        In mode=\033[1m'url'\033[0m, (default) source is a url to a past stream/VOD. 
        We currently only support links from: {', '.join(SUPPORTED_PLATFORMS)}. The link must
        be to the original stream/VOD with that attached chat replay. 

        In mode=\033[1m'chatfile'\033[0m, source is a filepath to a .json containing \033[3mraw chat data\033[0m, 
        produced by Xenonva's chat-downloader, or by this program's `--save-chatfile-output` flag. NOTE: the --platform argument is required
        when using this mode.

        In mode=\033[1m'reanalyze'\033[0m, source is a filepath to a .json file previously produced by this program which contains \033[3mexisting sample data to reanalyze\033[0m.
        (Highlights and spikes are regenerated, the existing samples are not affected).""")

    parser.add_argument("--platform", type=str, choices=dict.keys(SUPPORTED_PLATFORMS_SHORTHANDS), help="""
    When reading from a chatfile, specify the platform the chat was downloaded from. 
    By default, Xenova's chat downloader does not store this information with the chat data so it must be manually specified. 
    If the incorrect platform is entered, site-specific data will be innacurate but the program will still run and analyze common attributes.""")

    # Mode arguments
    mode_group = parser.add_argument_group("Program Behavior (Mode)")
    # mutex_mode_group = mode_group.add_mutually_exclusive_group()
    mode_group.add_argument("--mode", "-m", default="url", choices=["url", "chatfile", "reanalyze"], type=str,\
        help="""R|The program can be run in three modes:

        \033[3mNOTE: All modes result in chat analytics output as a .json file.\033[0m

        \033[1m\'url\'\033[0m mode (default) downloads raw chat data from an appropriate source, processes the raw chat data into samples, and then analyzes the samples.

        \033[1m\'chatfile\'\033[0m mode reads raw chat data from a .json file, processes the raw chat data into samples, and then analyzes the samples.
        (We accept raw chat files produced by Xenonva's chat-downloader, or by this program through '--save-chatfile-output').

        \033[1m\'reanalyze\'\033[0m mode reads existing sample data from a .json file produced by this program in a previous run, and recalculates ONLY the post-processed data based on the existing samples. 
        (Highlights and spikes are regenerated, the existing samples are not affected).
        \n""")
    # TODO: Do we restirct use with mode=chatfile, or just admit that it creates a duplicate/slightly different file?
    # TODO: Can't use with reanalyze mode because we don't have access to the chat data, so maybe we just enforce that its a url-only command
    # TODO: Add argument to specify output of the saved chatfile
    mode_group.add_argument("--save-chatfile-output", "-sc", type=str, help="""
    Filepath of the raw chat data to save. If downloading chat data from a URL, 
    save the raw chat data to the provided filepath in addition to processing it, 
    so that the raw data can be \033[3mfully\033[0m reprocessed and analyzed again quickly (using mode='chatfile').
    NOTE: Chatfiles are *much* larger in comparison to the analytics file.  
    NOTE: json file extension is enforced because it affects the content that the chat downloader writes to the file.""")

    # Processing Arguments
    sampling_group = parser.add_argument_group("Processing (Sampling)")
    sampling_group.add_argument("--interval", "-i" , default=5, type=check_interval, help="""
            The time interval (in seconds) at which to compress datapoints into samples. i.e. Duration of the samples. The smaller the interval, the more 
            granular the analytics are. At interval=5, each sample contains 5 seconds of cumulative data.
            *(With the exception of the last sample, which may be shorter than the interval).*""")
    sampling_group.add_argument("--print-interval", default=100, type=int, help="Number of messages between progress updates to the console. If <= 0, progress is not printed.")
    
    
    # Post Processing (Analyzing) Arguments
    postprocess_group = parser.add_argument_group("Post Processing (Analyzing)")
    postprocess_group.add_argument("--highlight-percentile", "-ep", default=93.0, type=check_percentile_float, help="""
    A number between 0 and 100, representing the cutoff percentile that a sample's attribute must meet to be considered a 'highlight' of the chatlog. 
    Samples in the top HIGHLIGHT_PERCENTILE%% of the selected highlight metric will be considered high-engagement samples and included within the constructed highlights. 
    The larger the percentile, the greater the metric requirement before being reported. If 'highlight-percentile'=93.0, only samples in the 93rd percentile (top 7.0%%) of the selected metric will be included in the highlights.
    """)
    metric_choices = ["usersPSec","chatsPSec","activityPSec"] # update metric_to_field map when adding new metrics
    postprocess_group.add_argument("--highlight-metric", "-em", default=metric_choices[0], choices=metric_choices, type=str, help=f"""R|\
    The metric to use for engagement analysis when constructing highlights. Samples in the top HIGHLIGHT_PERCENTILE%% of the selected metric will be considered high-engagement samples and included within the constructed highlights. 
    Each highlight metric choice corresponds to a datapoint for each sample. \n
    \033[1m\'{metric_choices[0]}\'\033[0m compares samples based off of the average number unique users that send a chat per second of the sample.\n
    \033[1m\'{metric_choices[1]}\'\033[0m compares samples based off of the average number of chats per second of the sample (not necessarily sent by unique users).\n 
    \033[1m\'{metric_choices[2]}\'\033[0m compares samples based off of the average number of any type of message that appears in the chat per second of the sample.\n 
    """)

    # TODO: spike sensitivity
    # TODO: spike metric

    # mutex_postprocess_group = postprocess_group.add_mutually_exclusive_group()
     # mutex_postprocess_group.add_argument("--spike-time", default=120, type=check_positive_int, help="Specify the total amount of cumulative spike time (in seconds) that we want output.")
    # TODO: More settings for finding spike. Sensitivity based, or "top-5 based" or...?

    # TODO: Allow user to specify which field they want spike detection on (possibly multiple fields resulting in multiple types of spikes in the list)

   
    # Output Arguments
    output_group = parser.add_argument_group("Output")
    output_group.add_argument("--description", "-d" , type=str, help="R|A description included in the output file to help distinguish it from other output files.\nex: -d \"Ludwig product announcement, small intervals\"")
    output_group.add_argument("--output", "-o", type=str, help="""The filepath to write the output to. If not specified, the output is written to '[MEDIA TITLE].json.' 
                                                    If the provided file path does not end in '.json', the '.json' file extension is appended automaticaly to the filepath (disable with --nojson).""")
    output_group.add_argument("--nojson", action="store_true", help="Disable the automatic appending of the '.json' file extension to the provided output filepath.")
    # TODO: Add a console output group (verbose, quiet, progress update, etc...)

    debug = parser.add_argument_group('Debugging')
    debug.add_argument('--debug','-db', action='store_true', help='Enable debug mode (debug info is printed)')
    debug.add_argument('--break','-b', type=int, default=-1, help='Stop processing messages after BREAK number of messages have been processed. No effect if val < 0')

    args = parser.parse_args()
    kwargs = args.__dict__

    # Argument dependency-checks:
    if(kwargs['mode'] == 'chatfile' and kwargs['platform']== None):
        parser.error('When reading from a chatfile, you must specify the platform the chatfile is from with --platform argument.')
        # TODO: Add description of this to the chatfile desc and add the actual platform arg itself
    if(kwargs['save_chatfile_output']):  
        if(kwargs['mode'] != 'url'):
            parser.error('The --save-chatfile-output flag can only be used in mode=\033[1m\'url\'\033[0m.')
        if(not kwargs['save_chatfile_output'].endswith('.json')):
            kwargs['save_chatfile_output'] += '.json'
    if(kwargs['output']):
        if(not kwargs['output'].endswith('.json') and not kwargs['nojson']):
            kwargs['output'] += '.json'
    # TODO: Interval should not be allowed with mode = reanalyze (clarify again what reanalyze is for)
    # TODO: Low percentiles result in no highlights... why?

    run(**kwargs)




# Some testing URLs
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


# chat_analyzer 'https://www.twitch.tv/videos/1522574868' --print-interval 100 -i 10


# chat_analyzer 'https://www.twitch.tv/videos/1289325547' -o output/analyze/markiplier_peen.json -sc output/raw/markiplier_peen_chat.json
# chat_analyzer output/analyze/markiplier_peen.json -m reanalyze -o output/analyze/markiplier_peen_reanalyzed.json