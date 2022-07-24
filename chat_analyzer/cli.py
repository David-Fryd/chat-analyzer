import argparse

from chat_analyzer import run

def main():
    print("this is the CLI main fxn TODO: Remove this print")

    parser = argparse.ArgumentParser()

    parser.add_argument("url", type=str, help="URL of the chat to analyze")
    parser.add_argument("--interval", default=5, type=int, help="Interval of the chat to analyze")


    args = parser.parse_args()

    run(**args.__dict__)