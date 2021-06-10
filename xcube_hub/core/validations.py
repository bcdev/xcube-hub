import os

from xcube_hub import api

REQUIRED_ENV_VARS = [
    "AUTH0_USER_MANAGEMENT_CLIENT_ID",
    "AUTH0_USER_MANAGEMENT_CLIENT_SECRET",
    "SH_CLIENT_ID",
    "SH_CLIENT_SECRET",
    "SH_INSTANCE_ID",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "XCUBE_DOCKER_IMG",
    "XCUBE_HUB_DOCKER_PULL_POLICY",
    "XCUBE_HUB_CACHE_PROVIDER",
    "XCUBE_HUB_REDIS_HOST",
    "XCUBE_WEBAPI_URI",
    "XCUBE_HUB_CALLBACK_URL",
    "XCUBE_HUB_OAUTH_AUD",
    "XCUBE_HUB_TOKEN_SECRET",
    "XCUBE_HUB_OAUTH_USER_MANAGEMENT_AUD"
]


def validate_env():
    for var in REQUIRED_ENV_VARS:
        val = os.getenv(var, None)
        if val is None:
            raise api.ApiError(500, f"Env var {var} required.")

    return True
