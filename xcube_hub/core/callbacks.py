from botocore.exceptions import ClientError

from xcube_hub import api
from xcube_hub.api import get_json_request_value
from xcube_hub.cfg import Cfg
from xcube_hub.core.costs import get_size_and_cost
from xcube_hub.core.punits import subtract_punits
from xcube_hub.keyvaluedatabase import KeyValueDatabase

from xcube_hub.typedefs import AnyDict, JsonObject


def get_callback(user_id: str, cubegen_id: str) -> JsonObject:
    try:
        cache = KeyValueDatabase.instance()
        res = cache.get(user_id + '__' + cubegen_id)

        if not res:
            return {}

        if 'progress' in res:
            return res['progress']
        else:
            return res
    except TimeoutError as r:
        raise api.ApiError(400, r.strerror)


def put_callback(user_id: str, cubegen_id: str, value: AnyDict, email: str):
    if not value or 'state' not in value:
        raise api.ApiError(401, 'Callbacks need a "message" as well as a "state"')

    try:
        print(f"Calling progress for {cubegen_id}.")
        kvdb = KeyValueDatabase.instance()
        kv = kvdb.get(user_id + '__' + cubegen_id)

        if kv and 'progress' in kv and isinstance(kv['progress'], list):
            kv['progress'].append(value)
        else:
            kv = dict(progress=[value])

        res = kvdb.set(user_id + '__' + cubegen_id, kv)

        sender = get_json_request_value(value, "sender", str)
        state = get_json_request_value(value, 'state', dict)

        if sender == 'on_end':
            if 'error' not in state:
                processing_request = kvdb.get(user_id + '__' + cubegen_id + '__cfg')
                input_config = processing_request['input_configs']

                store_id = input_config[0]['store_id']

                store_id = store_id.replace('@', '')
                datastore = Cfg.get_datastore(store_id)
                punits_requests = get_size_and_cost(processing_request=processing_request, datastore=datastore)

                subtract_punits(user_id=email, punits_request=punits_requests)

        return kv
    except (TimeoutError, ClientError) as e:
        raise api.ApiError(400, str(e))
