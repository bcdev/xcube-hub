import os
from typing import Sequence, Optional

from xcube_hub.controllers.oauth import create_token


def create_test_token(permissions: Optional[Sequence] = None,
                      audience: Optional[str] = "https://xcube-gen.brockmann-consult.de/api/v2/"):
    if permissions is None:
        permissions = ["manage:users", "manage:cubegens"]

    claims = {
        "iss": "https://xcube-gen.brockmann-consult.de/",
        "aud": [audience],
        "scope": permissions,
        "gty": "client-credentials",
        "email": "test@mail.com",
        "permissions": permissions
    }

    os.environ['XCUBE_HUB_TOKEN_SECRET'] = '+k5kLdMEX1o0pfYZlieAIjKeqAW0wh+5l9PfReyoKyZqYndb2MeYHXGqqZ2Uh1zZATCHMwgyIirYSVDAi9N6izWBYAG/GGfS3VJFA2FEg+YMQSHbhCTdG+/7p7XvltFyO8MPLhU5LFDWLc2rZCOliSBocfnYrM5AaHD7JsjUqR+Ej3vVcfWAHPAyp66m/1TaD6svCuDcdXN09I0UJ+10Q/Ps2Vz9qHKhK6oW8gqXHjG8+jZvjjeH29LLkPdYHM5nofyDMumJYRrHBuRcnCt4EtDUJurH4LizPCvrAbMarc/03w1+vu+LEpRR67O7N7zdaXBkPc4VRwF5aLCh5MLeEg==]'
    os.environ["XCUBE_HUB_OAUTH_USER_MANAGEMENT_AUD"] = "https://test"
    os.environ["XCUBE_HUB_OAUTH_AUD"] = "https://xcube-gen.brockmann-consult.de/api/v2/"
    token = create_token(claims=claims)

    return claims, token
