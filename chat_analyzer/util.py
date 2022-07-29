def dprint(should_print: bool, s: str):
    """Simple styled debug printer
    """
    if(should_print):
        print(f"\033[1;32m[DEBUG]:\033[3m {s}\033[0m")