import os

import yaml
from jsonschema import validate, ValidationError, SchemaError

from xcube_hub import util, api
from xcube_hub.typedefs import JsonObject


class CfgError(ValueError):
    pass


class Cfg:
    _datapools_cfg = None
    _services_cfg = None

    @classmethod
    def get_datastore(cls, datastore: str):
        try:
            return cls._datapools_cfg[datastore]
        except (TypeError, KeyError) as e:
            raise api.ApiError(400,
                               f"Error: Could not load datastore configuration. Datastore {datastore} not in config.")

    @classmethod
    def get_service(cls, service: str):
        try:
            return cls._services_cfg[service]
        except KeyError as e:
            raise api.ApiError(400,
                               f"Error: Could not load service configuration. Service {service} not in config.")

    @classmethod
    def get_services(cls):
        try:
            return cls._services_cfg.keys()
        except AttributeError as e:
            raise api.ApiError(400,
                               f"Error: Could not load service configuration. No services configured.")

    @classmethod
    def _validate_datastores(cls, data_pools: JsonObject):
        data_pools_cfg_schema_file = util.maybe_raise_for_env("XCUBE_HUB_CFG_DATAPOOLS_SCHEMA")
        data_pools_cfg_dir = util.maybe_raise_for_env("XCUBE_HUB_CFG_DIR")
        try:
            with open(os.path.join(data_pools_cfg_dir, data_pools_cfg_schema_file), "r") as f:
                data_pools_schema = yaml.safe_load(f)
        except FileNotFoundError:
            raise api.ApiError(404, "Could not find data pools configuration")
        try:
            cls._validate(js=data_pools, schema=data_pools_schema)
        except (ValueError, ValidationError, SchemaError) as e:
            raise api.ApiError(400, "Could not validate data pools configuration. " + str(e))

        return True

    @classmethod
    def _validate_services(cls, services: JsonObject):
        cfg_schema_file = util.maybe_raise_for_env("XCUBE_HUB_CFG_SERVICES_SCHEMA")
        cfg_dir = util.maybe_raise_for_env("XCUBE_HUB_CFG_DIR")
        try:
            with open(os.path.join(cfg_schema_file, cfg_dir), "r") as f:
                schema = yaml.safe_load(f)
        except FileNotFoundError:
            raise api.ApiError(404, "Could not find services configuration")

        cls._validate(js=services, schema=schema)

        return True

    @classmethod
    def _validate(cls, js: JsonObject, schema: JsonObject):
        try:
            validate(instance=js, schema=schema)
        except (ValueError, ValidationError, SchemaError) as e:
            raise api.ApiError(400, "Could not validate data pools configuration. " + str(e))

        return True

    @classmethod
    def _load_datastores(cls):
        if not cls._datapools_cfg:
            data_pools_cfg_file = util.maybe_raise_for_env("XCUBE_HUB_CFG_DATAPOOLS")
            data_pools_cfg_dir = util.maybe_raise_for_env("XCUBE_HUB_CFG_DIR")
            try:
                with open(os.path.join(data_pools_cfg_dir, data_pools_cfg_file), 'r') as f:
                    cls._datapools_cfg = yaml.safe_load(f)
                    cls._validate_datastores(cls._datapools_cfg)
            except FileNotFoundError:
                raise api.ApiError(404, "Could not find data pools configuration")

    @classmethod
    def _load_services(cls):
        services_cfg_file = util.maybe_raise_for_env("XCUBE_HUB_CFG_SERVICES")
        cfg_dir = util.maybe_raise_for_env("XCUBE_HUB_CFG_DIR")
        if not cls._services_cfg:
            try:
                with open(os.path.join(cfg_dir, services_cfg_file), 'r') as f:
                    cls._services_cfg = yaml.safe_load(f)
                    cls._validate_datastores(cls._datapools_cfg)
            except FileNotFoundError:
                raise api.ApiError(404, "Could not find data pools configuration")

    @classmethod
    def load_config(cls):
        cls._load_datastores()
        # cls._load_services()