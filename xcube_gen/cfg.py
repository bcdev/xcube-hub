import json
import os
import threading
from datetime import datetime
from pprint import pprint
from typing import Sequence, Optional

from kubernetes import client

from xcube_gen.types import AnyDict


class CfgError(ValueError):
    pass


class Cfg:
    _config_lock = threading.Lock()
    _config_loaded = False

    def __init__(self):
        self._load_config_once()

    @classmethod
    def _load_config_once(cls):
        if not cls._config_loaded:
            cls._config_lock.acquire()
            if not cls._config_loaded:
                cls._load_config()
                cls._config_loaded = True
            cls._config_lock.release()

    @classmethod
    def _load_config(cls):
        from kubernetes import config
        if os.environ.get('RUN_LOCAL'):
            print("Kubernetes configured to run locally.")
            config.load_kube_config()
        else:
            config.load_incluster_config()


CFG = Cfg()
