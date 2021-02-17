#!/usr/bin/env python3
import os

import connexion
from dotenv import load_dotenv

from xcube_hub import encoder
from xcube_hub.k8scfg import K8sCfg
from xcube_hub.keyvaluedatabase import KeyValueDatabase


app = connexion.App(__name__, specification_dir='./resources/')


def main():
    load_dotenv()
    K8sCfg.load_config_once()
    cache_provider = os.environ.get('XCUBE_HUB_CACHE_PROVIDER', 'inmemory')
    KeyValueDatabase.instance(provider=cache_provider)

    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'xcube Generation API'},
                pythonic_params=True)

    app.run(port=8080)


if __name__ == '__main__':
    main()
