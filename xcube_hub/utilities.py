import os
import re
from typing import Optional, Sequence

from kubernetes import client


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


def load_env_by_regex(regex: Optional[str] = None) -> Sequence[client.V1EnvVar]:
    p = re.compile(regex or '')

    return [client.V1EnvVar(name=k, value=v) for k, v in os.environ.items() if regex is None or p.match(k)]
