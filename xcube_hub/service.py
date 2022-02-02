import os

import connexion
import flask_cors
from connexion.decorators.validation import ParameterValidator, RequestBodyValidator
from dotenv import load_dotenv

from xcube_hub import encoder
from xcube_hub.cfg import Cfg
from xcube_hub.core.validations import validate_env
from xcube_hub.geoservice import GeoService
from xcube_hub.k8scfg import K8sCfg
from xcube_hub.keyvaluedatabase import KeyValueDatabase
from logging.config import dictConfig


dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(levelname).1s %(asctime)s  %(name)s] %(message)s',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
    },
    'loggers': {
        'xcube-hub': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


class CustomRequestBodyValidator(RequestBodyValidator):
    def __init__(self, schema, consumes, api, is_null_value_valid=False, validator=None,
                 strict_validation=False):
        super().__init__(schema, consumes, api, is_null_value_valid, validator, strict_validation)

    def validate_schema(self, data, url):
        pass


validator_map = {
    'body': CustomRequestBodyValidator,
    'parameter': ParameterValidator
}


def create_app():
    load_dotenv()
    validate_env()

    K8sCfg.load_config_once()
    Cfg.load_config()

    GeoService.instance(provider="geoserver")

    cache_provider = os.environ.get('XCUBE_HUB_CACHE_PROVIDER', 'inmemory')
    # specification_dir = maybe_raise_for_env("XCUBE_HUB_CFG_DIR", './resources/')
    KeyValueDatabase.instance(provider=cache_provider)

    connexion_app = connexion.App(__name__, specification_dir='./resources/')

    return connexion_app


app = create_app()


def attach_debugger():
    xcube_hub_debug = os.getenv('XCUBE_HUB_DEBUG', "0")

    if xcube_hub_debug == "1":
        print("Attaching Debugger")

        import pydevd_pycharm
        pydevd_pycharm.settrace('localhost', port=9000, stdoutToServer=True, stderrToServer=True)
        print("Attached Debugger")


def start(host: str = '0.0.0.0', port: int = 8080, debug: bool = False):
    attach_debugger()

    debug = debug or int(os.getenv('XCUBE_HUB_DEBUG', False))
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'xcube Generation API'},
                pythonic_params=True,
                validate_responses=False)
    flask_cors.CORS(app.app)
    app.run(host=host, port=port, debug=False, use_reloader=False)
