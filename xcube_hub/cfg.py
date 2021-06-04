import os

import yaml

from xcube_hub import util, api


class CfgError(ValueError):
    pass


class Cfg:
    _services_cfg = None

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
    def _load_services(cls):
        services_cfg_file = util.maybe_raise_for_env("XCUBE_HUB_CFG_SERVICES")
        cfg_dir = util.maybe_raise_for_env("XCUBE_HUB_CFG_DIR")
        if not cls._services_cfg:
            try:
                with open(os.path.join(cfg_dir, services_cfg_file), 'r') as f:
                    cls._services_cfg = yaml.safe_load(f)

            except FileNotFoundError:
                raise api.ApiError(404, "Could not find data pools configuration")

    @classmethod
    def load_config(cls):
        cls._load_services()
