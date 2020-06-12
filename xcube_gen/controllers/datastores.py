import json
import os.path

from xcube_gen import api
from xcube_gen.xg_types import JsonObject


def get_datastores() -> JsonObject:
    datastores_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'datastores.json')
    with open(datastores_path) as fp:
        try:
            return json.load(fp)
        except json.decoder.JSONDecodeError as e:
            raise api.ApiError(401, str(e))

