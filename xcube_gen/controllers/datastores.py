import json
import os.path

from xcube_gen.types import AnyDict


def get_datastores() -> AnyDict:
    datastores_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'datastores.json')
    with open(datastores_path) as fp:
        return json.load(fp)
