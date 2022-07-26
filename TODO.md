# Chat Analyzer TODO

Some Todos have associated places in the codebase where a comment exists with the TODO's hash, making it easy to find/location the parts in the code that have already been identified as associated with the TODO.

## High Priority
- Standardize logging/printing of info/output/error messages
- Print output destination on completion
- In addition to regular & integrated processing, add 2 modes:
  - Add option/flag to re-process a local output file for spikes
  - Add option to specificy input chat-downloaded file (helpful for analysis of diff sample lengths)

## Medium Priority
- Additional tracking statistics
  - Highest 1,5,10 min periods of engangement (potentially more/different periods) (Highlights
  - Average messages per chatter (not all users, just average among active chatters) (NOT avg chat per viewers because we don't know how many viewers there are)
  - Best/(Top 5) chatters.
  - Median messages per chatter
  - Use statistics library to find outliers, report median, std dev, etc... 
  - Go through messsage types to figure out what we should be tracking in the ChatAnalytics
- Additional tracking for samples:
  - How many chatters spoke that haven't spoken in the last X samples/minutes/interval? (Not critical)
- Develop meaningful error codes whenever `exit()` is invoked. (See chat_analyzer.py, and maybe other places)

## Low Priority
- Control message types that we analyze/download based on CLI. (chat_analyzer.py TODO#56ab7)

## In the future...
- Semantic analysis using DL
  - Standard: Which parts of chat are pos/negative/...?
  - Case-Specific: DL trained on stream chats specifically- exciting/lmao get rekt/wholesome/ other classifications pertinent to stream