import re # REGEX used in string cleaning

def dprint(should_print: bool, s: str):
    """Simple styled debug printer
    """
    if(should_print):
        print(f"\033[1;32m[DEBUG]:\033[3m {s}\033[0m")

def remove_non_alpha_numeric(s: str) -> str:
    """Remove non-alphanumeric characters from a string and replaces all spacebars with underscores
    (Useful for normalizing the title of a video before turning it into a filename)
    """
    retString = "".join(c for c in s if c.isalnum() or c ==' ')
    return retString.replace(' ', '_')