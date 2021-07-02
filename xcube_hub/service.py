#!/usr/bin/env python3
import os

import connexion
import flask_cors
from dotenv import load_dotenv

from xcube_hub import encoder
from xcube_hub.cfg import Cfg
from xcube_hub.core.validations import validate_env
from xcube_hub.geoservice import GeoService
from xcube_hub.k8scfg import K8sCfg
from xcube_hub.keyvaluedatabase import KeyValueDatabase


def create_app():
    load_dotenv()
    validate_env()

    K8sCfg.load_config_once()
    Cfg.load_config()

    GeoService.instance(provider="geoserver")

    cache_provider = os.environ.get('XCUBE_HUB_CACHE_PROVIDER', 'inmemory')
    # specification_dir = maybe_raise_for_env("XCUBE_HUB_CFG_DIR", './resources/')
    KeyValueDatabase.instance(provider=cache_provider)

    return connexion.App(__name__, specification_dir='./resources/')


app = create_app()


def attach_debugger():
    xcube_hub_debug = os.getenv('XCUBE_HUB_DEBUG', "0")
    if xcube_hub_debug == "1":
        import pydevd_pycharm
        pydevd_pycharm.settrace('0.0.0.0', port=9000, stdoutToServer=True, stderrToServer=True)


def start(host: str = '0.0.0.0', port: int = 8080, debug: bool = False):
    attach_debugger()

    debug = debug or int(os.getenv('XCUBE_HUB_DEBUG', False))
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'xcube Generation API'},
                pythonic_params=True)
    flask_cors.CORS(app.app)
    app.run(host=host, port=port, debug=debug, use_reloader=False)

