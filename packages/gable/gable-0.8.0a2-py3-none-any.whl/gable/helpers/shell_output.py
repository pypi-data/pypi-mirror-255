def shell_linkify(url: str, title: str) -> str:
    """Returns a string that will display as a clickable link in the terminal"""
    return f"\033]8;;{url}\a{title}\033]8;;\a"
