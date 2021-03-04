import yaml
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from xcube_hub import api
from xcube_hub.util import maybe_raise_for_env


def get_stores_from_file():
    store_fn = maybe_raise_for_env('XCUBE_GEN_DATA_POOLS_PATH')

    try:
        with open(store_fn, 'r') as f:
            stores = yaml.safe_load(f)

            try:
                stores = {k: {'title': v['title'], 'store_id': v['store_id'],
                              'description': v['description'] if 'description' in v else ''} for k, v in stores.items()}
            except KeyError as e:
                raise api.ApiError(400, "Error when loading datapools. " + str(e))

            return stores

    except (TypeError, FileNotFoundError, ParserError, ScannerError) as e:
        raise api.ApiError(400, str(e))
