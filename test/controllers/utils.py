from typing import Sequence, Optional, Dict

from xcube_hub.core.oauth import create_token


def create_test_token(permissions: Optional[Sequence] = None,
                      audience: Optional[str] = "https://xcube-gen.brockmann-consult.de/api/v2/",
                      claims: Optional[Dict] = None):
    if permissions is None:
        permissions = ["manage:users", "manage:cubegens"]

    claims = claims or {
        "iss": "https://xcube-gen.brockmann-consult.de/",
        "aud": [audience],
        "scope": permissions,
        "gty": "client-credentials",
        "email": "test@mail.com",
        "sub": "test@mail.com",
        "permissions": permissions
    }

    token = create_token(claims=claims)

    return claims, token


