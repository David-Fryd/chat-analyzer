# Chat Analyzer TODO

## High Priority
- Standardize logging/printing of info/output/error messages. Look at print() and logging. calls.
- Print output destination on completion
- In addition to regular & integrated processing, add 2 modes:
  - Add option/flag to re-process a local output file for spikes
  - Add option to specificy input chat-downloaded file (helpful for analysis of diff sample lengths)
- Spike Percentile based on CLI args, also have a way to determine percentile that equals x mins of videos
- Define output file, and print where file is created/output upon completion

## Medium Priority
- Add debug early break in process_chatlog in dataformat
- Find other types we currently don't handle and figure out how to do so. i.e. `sponsorships_gift_redemption_announcement`, `raid`, etc...
- Implement `get_engagement_sections`
- Find way to prevent private fields (fields preceeded w _ in dataformat) from being serialized and output in the JSON. (For both ChatAnalytics abd Sample)
  - POTENTIAL SOL: Maybe set them = to sets {}, it seems that the constants defined as sets are ignored and automatically not output in the JSON?... But also have historically had set issues in the past... idk (:
  - `del` and `delattr` don't work, so we temporarily just remove all of the data from the fields instead of removing the fields themselves
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
- Improve spike descriptions
- Control message types that we analyze/download based on CLI. (Edit chat_download_settings before passing to the chat downloader)
- Prune redundant fields from `dataformat` classes, for example: `duration` and `duration_text` fields from `Highlight` when we ensure naive front-end graphing solution
- Spike percentile field
  - float: This spike is in the top 'percentile'% of all spikes of the same 'type'
  - Remove or implement (implementation would be pretty time-consuming for not a whole lot of gain?)
- Implement other types of highlights
- Implement spike percentiles:
  - spike_percentiles: dict[str: list[int]] (Implement or remove)
  - For every unique spike 'type' in spikes, we report the percentile values for commonly saught-after percentiles. For example, if spikes were calculated for the 'avgUniqueUsersPerSecond' field, spike_percentiles will contain an entry: 'avgUniqueUsersPerSecond' -> [0th, 25th, 50th, 75th, 90th, 95th, 99th] (where each of the vals is the percentile val?)
- Implement run-length encoding for `create_new_sample()`
  - In the current implementation, there could exist consecutive samples with 0 activity (or identical, but less likely), which are easily compressed. However, this uncompressed approach makes naively graphing the points easier, which is a primary objective of the output of this program.
  - A sequence of identical no-activity samples could eventually be compressed into 1 or 3 samples. (3 sample approach helps preserve naive graphing):
    - 1 sample apprch: 1 sample consumes all of the consecutive identical samples and modifies start/end/duration accordingly
    - 3 sample apprch: 3 sample approach preserves first and last sample, and combines intermediate samples. That way the slope into/out of the silence interval is preserved.
    - Other potential options, but these are the ones we have considered that are not terribly complex
            

## In the future...
- Semantic analysis using DL
  - Standard: Which parts of chat are pos/negative/...?
  - Case-Specific: DL trained on stream chats specifically- exciting/lmao get rekt/wholesome/ other classifications pertinent to stream