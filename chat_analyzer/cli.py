import argparse


from analyzer import run, MAX_INTERVAL, MIN_INTERVAL
from dataformat import SUPPORTED_PLATFORMS

program_description = "A program that analyzes chat logs from previous live streams and reports useful data about activity over the stream's lifetime."

MAX_INTERVAL
MIN_INTERVAL

def check_interval(interval):
    """
    Based on the MAX_INTERVAL and MIN_INTERVAL from chat_analyzer.py,
    ensure that the entered interval respects that boundary"""
    interval = int(interval)
    if interval < MIN_INTERVAL:
        raise argparse.ArgumentTypeError(f"Interval must be at least {MIN_INTERVAL}")
    if interval > MAX_INTERVAL:
        raise argparse.ArgumentTypeError(f"Interval must be at most {MAX_INTERVAL}")
    return interval

def main():
    parser = argparse.ArgumentParser(program_description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser._positionals.title = 'Required Arguments'
    parser._optionals.title = 'Optional Arguments'
    # parser._subparsers.title = 'Subcommands'

    # TODO: Add subparser for different modes (instead of having a --modes thing)?
    # https://stackoverflow.com/questions/8250010/argparse-identify-which-subparser-was-used/9286586#9286586
    # https://stackoverflow.com/questions/17073688/how-to-use-argparse-subparsers-correctly

    parser.add_argument("source", type=str,\
        help=f"""A url to a past stream/VOD. We currently only support links from: {', '.join(SUPPORTED_PLATFORMS)}.
        In --mode=='chatfile' or 'reprocess', source is a filepath to a 
        .json raw chat log produced by Xenonva's chat-downloader, 
        or a .json output file previously produced by this program (respectively).""")

    mg = parser.add_argument_group("Program Behavior (Mode)")
    mode_group = mg.add_mutually_exclusive_group()
    mode_group.add_argument("--mode", default="url", choices=["url", "chatfile", "reprocess"], type=str,\
        help="""The program can be run in three modes:
        \033[1m\'url\'\033[0m mode (default) will download the chatlog and simultaneously process the chats as they are downloaded.
        \033[1m\'chatfile\'\033[0m mode reads from a .json file with raw chat data produced by Xenonva's chat-downloader.
        \033[1m\'reprocess\'\033[0m mode reads from a .json file produced by this program in a previous run, and recalculates the post-processed data based on the existing samples.""")
    
    
    parser.add_argument("--interval", default=5, type=check_interval, help="Interval of the chat to analyze")

    # TODO: Add mutually exclusive 'MODE
        # standard has everything built in
        # re-process an old output file
        # process a downloaded chat json file produced separately by the chat-downloader

    # TODO: Add sample size, etc...

    # TODO: Settings for finding spike. Sensitivity based, or "top-5 based" or...?

    # TODO: Add a console output group (verbose, quiet, progress update, etc...)
    # We print progress of the download/process every UPDATE_PROGRESS_INTERVAL messages
    # if <=0, we don't print progress
    parser.add_argument("--print-proggress-interval", "-ppi", default=1000, type=int, help="Interval of progress printing TODO: Add better description")

    # output_group = parser.add_argument_group("Output")

    args = parser.parse_args()

    run(**args.__dict__)