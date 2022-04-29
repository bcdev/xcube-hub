import os

from xcube_hub import api

REQUIRED_ENV_VARS = [
    "XCUBE_HUB_OAUTH_USER_MANAGEMENT_CLIENT_ID",
    "XCUBE_HUB_OAUTH_USER_MANAGEMENT_CLIENT_SECRET",
    "XCUBE_HUB_CALLBACK_URL",
    "XCUBE_HUB_OAUTH_AUD",
    "XCUBE_HUB_OAUTH_HS256_SECRET",
    "XCUBE_HUB_OAUTH_USER_MANAGEMENT_AUD"
]


def validate_env():
    for var in REQUIRED_ENV_VARS:
        val = os.getenv(var, None)
        if val is None:
            raise api.ApiError(500, f"Env var {var} required.")

    return True
