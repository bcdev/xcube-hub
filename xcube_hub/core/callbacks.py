from xcube_hub import api
from xcube_hub.api import get_json_request_value
from xcube_hub.core.costs import get_size_and_cost
from xcube_hub.core.punits import subtract_punits
from xcube_hub.keyvaluedatabase import KeyValueDatabase

from xcube_hub.typedefs import AnyDict


def put_callback(user_id: str, cubegen_id: str, value: AnyDict, email: str):
    if not value or 'state' not in value:
        raise api.ApiError(401, 'Callbacks need a "message" as well as a "state"')

    try:
        print(f"Calling progress for {cubegen_id}.")
        kvdb = KeyValueDatabase.instance()
        kv = kvdb.get(user_id + '__' + cubegen_id)
        if not kv:
            kvdb.set(user_id + '__' + cubegen_id, value)

        if kv and 'progress' in kv:
            kv['progress'].append(value)
        if kv and 'progress' not in kv:
            kv['progress'] = [value]
        else:
            kv = dict(progress=[value])

        res = kvdb.set(user_id + '__' + cubegen_id, kv)

        sender = get_json_request_value(value, "sender", str)
        state = get_json_request_value(value, 'state', dict)

        if sender == 'on_end':
            if 'error' not in state:
                processing_request = kvdb.get(user_id + '__' + cubegen_id + '__cfg')
                punits_requests = get_size_and_cost(processing_request)

                subtract_punits(user_id=email, punits_request=punits_requests)

        return res
    except TimeoutError as e:
        raise api.ApiError(401, e.strerror)
