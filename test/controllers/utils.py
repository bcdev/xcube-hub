import os
from typing import Sequence, Optional, Dict

from dotenv import dotenv_values

from xcube_hub.core.oauth import create_token


def del_env(dotenv_path='.env'):
    for k, v in dotenv_values(dotenv_path=dotenv_path).items():
        del os.environ[k]


def create_test_token(permissions: Optional[Sequence] = None,
                      audience: Optional[str] = "https://xcube-gen.brockmann-consult.de/api/v2/",
                      iss: str = "https://xcube-gen.brockmann-consult.de/",
                      claims: Optional[Dict] = None):
    if permissions is None:
        permissions = ["manage:users", "manage:cubegens"]

    claims = claims or {
        "iss": iss,
        "aud": [audience],
        "scope": permissions,
        "gty": "client-credentials",
        "email": "test@mail.com",
        "sub": "test@mail.com",
        "permissions": permissions
    }

    token = create_token(claims=claims)

    return claims, token


