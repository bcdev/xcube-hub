import json
import os.path

import yaml

from xcube_hub import api
from xcube_hub.typedefs import JsonObject


def get_datastores() -> JsonObject:
    datastores_path = os.environ.get('XCUBE_GEN_DATASTORE_PATH', False)

    if datastores_path is False:
        datastores_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'datastores-sh.json')

    with open(datastores_path) as fp:
        try:
            return yaml.safe_load(fp)
        except json.decoder.JSONDecodeError as e:
            raise api.ApiError(401, str(e))

