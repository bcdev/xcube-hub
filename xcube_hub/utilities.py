import re


def raise_for_invalid_username(username: str) -> bool:
    valid = True
    if len(username) > 63:
        valid = False

    pattern = re.compile("[a-z0-9]([-a-z0-9]*[a-z0-9])?")
    if not pattern.fullmatch(username):
        valid = False

    if not valid:
        raise ValueError("Invalid user name.")

    return valid
