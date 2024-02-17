import re


def detect_locale_error(stderr):
    """
    Given a stderr output string `stderr`, will regex search for the locale errors

    Args:
        stderr:
            stderr text
    Returns:
        bool: True if the error appears to be a locale issue
    """
    match = r"(?i)(?:set|setting)\s?locale"

    return len(re.findall(match, stderr)) != 0
