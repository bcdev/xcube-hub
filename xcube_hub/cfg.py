import os
import threading


class CfgError(ValueError):
    pass


class Cfg:
    _config_lock = threading.Lock()
    _config_loaded = False

    @classmethod
    def load_config_once(cls):
        if not cls._config_loaded:
            cls._config_lock.acquire()
            if not cls._config_loaded:
                cls._load_config()
                cls._config_loaded = True
            cls._config_lock.release()

    @classmethod
    def _load_config(cls):
        from kubernetes import config
        if os.environ.get('XCUBE_GEN_API_RUN_LOCAL'):
            print("Kubernetes configured to run locally.")
            config.load_kube_config()
        else:
            config.load_incluster_config()

