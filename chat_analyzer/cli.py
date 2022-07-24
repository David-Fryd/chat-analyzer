import argparse

from chat_analyzer import run

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("url", type=str, help="URL of the chat to analyze")
    parser.add_argument("--interval", default=5, type=int, help="Interval of the chat to analyze")


    # TODO: Add sample size, etc...



    # TODO: Add a console output group (verbose, quiet, progress update, etc...)
    # We print progress of the download/process every UPDATE_PROGRESS_INTERVAL messages
    # if <=0, we don't print progress
    parser.add_argument("--print-proggress-interval", default=1000, type=int, help="Interval of progress printing")

    args = parser.parse_args()

    run(**args.__dict__)