import os

import yaml
from jsonschema import validate, ValidationError, SchemaError

from xcube_hub import util, api
from xcube_hub.typedefs import JsonObject


class CfgError(ValueError):
    pass


class Cfg:
    _datapools_cfg = None

    @classmethod
    def get(cls, datastore: str):
        try:
            return cls._datapools_cfg[datastore]
        except KeyError as e:
            raise api.ApiError(400,
                               f"Error: Could not load datastore configuration. Datastore {datastore} not in config.")

    @classmethod
    def _validate(cls, data_pools: JsonObject):
        data_pools_cfg_schema_file = util.maybe_raise_for_env("XCUBE_HUB_CFG_DATAPOOLS_SCHEMA")
        data_pools_cfg_dir = util.maybe_raise_for_env("XCUBE_HUB_CFG_DIR")
        try:
            with open(os.path.join(data_pools_cfg_dir, data_pools_cfg_schema_file), "r") as f:
                data_pools_schema = yaml.safe_load(f)
        except FileNotFoundError:
            raise api.ApiError(404, "Could not find data pools configuration")
        try:
            validate(instance=data_pools, schema=data_pools_schema)
        except (ValueError, ValidationError, SchemaError) as e:
            raise api.ApiError(400, "Could not validate data pools configuration. " + str(e))

        return True

    @classmethod
    def load_config(cls):
        if not cls._datapools_cfg:
            data_pools_cfg_file = util.maybe_raise_for_env("XCUBE_HUB_CFG_DATAPOOLS")
            data_pools_cfg_dir = util.maybe_raise_for_env("XCUBE_HUB_CFG_DIR")
            try:
                with open(os.path.join(data_pools_cfg_dir, data_pools_cfg_file), 'r') as f:
                    cls._datapools_cfg = yaml.safe_load(f)
                    cls._validate(cls._datapools_cfg)
            except FileNotFoundError:
                raise api.ApiError(404, "Could not find data pools configuration")
