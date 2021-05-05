import os

import yaml
from jsonschema import validate, ValidationError, SchemaError
from xcube_hub import api
from xcube_hub.util import maybe_raise_for_env

REQUIRED_ENV_VARS = [
    "AUTH0_USER_MANAGEMENT_CLIENT_ID",
    "AUTH0_USER_MANAGEMENT_CLIENT_SECRET",
    "SH_CLIENT_ID",
    "SH_CLIENT_SECRET",
    "SH_INSTANCE_ID",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "XCUBE_DOCKER_IMG",
    "XCUBE_DOCKER_WEBAPI_IMG",
    "XCUBE_HUB_DOCKER_PULL_POLICY",
    "XCUBE_HUB_CACHE_PROVIDER",
    "XCUBE_HUB_REDIS_HOST",
    "XCUBE_HUB_CALLBACK_URL",
    "XCUBE_HUB_OAUTH_AUD",
    "K8S_NAMESPACE",
    "XCUBE_HUB_TOKEN_SECRET",
    "XCUBE_HUB_OAUTH_USER_MANAGEMENT_AUD",
    "XCUBE_HUB_CFG_DIR",
    "XCUBE_HUB_CFG_DATAPOOLS",
    "XCUBE_HUB_CFG_DATAPOOLS_SCHEMA",
    "XCUBE_HUB_XCUBE_GEN_STATUS",
    "XCUBE_HUB_XCUBE_GEN_MESSAGE",
    "XCUBE_HUB_CATE_STATUS",
    "XCUBE_HUB_CATE_MESSAGE"
]


def validate_env():
    for var in REQUIRED_ENV_VARS:
        val = os.getenv(var, None)
        if val is None:
            raise api.ApiError(500, f"Env var {var} required.")

    return True


def validate_datapools():
    data_pools_cfg_file = maybe_raise_for_env("XCUBE_HUB_CFG_DATAPOOLS")
    data_pools_cfg_schema_file = maybe_raise_for_env("XCUBE_HUB_CFG_DATAPOOLS_SCHEMA")
    data_pools_cfg_dir = maybe_raise_for_env("XCUBE_HUB_CFG_DIR")

    try:
        with open(os.path.join(data_pools_cfg_dir, data_pools_cfg_file), 'r') as f:
            data_pools = yaml.safe_load(f)
        with open(os.path.join(data_pools_cfg_dir, data_pools_cfg_schema_file), "r") as f:
            data_pools_schema = yaml.safe_load(f)
    except FileNotFoundError:
        raise api.ApiError(404, "Could not find data pools configuration")

    try:
        validate(instance=data_pools, schema=data_pools_schema)
    except (ValueError, ValidationError, SchemaError) as e:
        raise api.ApiError(400, "Could not validate data pools configuration. " + str(e))

    return True
