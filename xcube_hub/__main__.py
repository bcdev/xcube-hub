#!/usr/bin/env python3
import os

import connexion
import flask_cors
from dotenv import load_dotenv

from xcube_hub import encoder
from xcube_hub.cfg import Cfg
from xcube_hub.core.validations import validate_env
from xcube_hub.k8scfg import K8sCfg
from xcube_hub.keyvaluedatabase import KeyValueDatabase


def create_app():
    load_dotenv()
    validate_env()

    Cfg.load_config()
    K8sCfg.load_config_once()
    cache_provider = os.environ.get('XCUBE_HUB_CACHE_PROVIDER', 'inmemory')
    KeyValueDatabase.instance(provider=cache_provider)

    return connexion.App(__name__, specification_dir='./resources/')


app = create_app()


def attach():
    werkzeug_run_main = os.getenv('WERKZEUG_RUN_MAIN', "0")
    xcube_hub_debug = os.getenv('XCUBE_HUB_DEBUG', "0")
    if int(werkzeug_run_main) and int(xcube_hub_debug):
        import pydevd_pycharm
        pydevd_pycharm.settrace('0.0.0.0', port=9000, stdoutToServer=True, stderrToServer=True)


def main():
    attach()
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'xcube Generation API'},
                pythonic_params=True)
    flask_cors.CORS(app.app)
    app.run(port=8080)


if __name__ == '__main__':
    main()
