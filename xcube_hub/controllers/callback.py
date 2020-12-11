from xcube_hub import api
from xcube_hub.api import get_json_request_value
from xcube_hub.keyvaluedatabase import KeyValueDatabase

from xcube_hub.controllers.users import subtract_processing_units
from xcube_hub.typedefs import JsonObject, AnyDict


def get_callback(user_id: str, job_id: str) -> JsonObject:
    try:
        cache = KeyValueDatabase.instance()
        res = cache.get(user_id + '__' + job_id)

        if not res:
            raise api.ApiError(404, 'Could not find any callback entries for that key.')

        return res
    except TimeoutError as r:
        raise api.ApiError(401, r.strerror)


def put_callback(user_id: str, job_id: str, value: AnyDict):
    if not value or 'state' not in value:
        raise api.ApiError(401, 'Callbacks need a "message" as well as a "state"')

    try:
        print(f"Calling progress for {job_id}.")
        kvdb = KeyValueDatabase.instance()
        kv = kvdb.get(user_id + '__' + job_id)
        if kv and 'progress' in kv:
            kv['progress'].append(value)
        if kv and 'progress' not in kv:
            kv['progress'] = [value]
        else:
            kv = dict(progress=[value])

        res = kvdb.set(user_id + '__' + job_id, kv)

        sender = get_json_request_value(value, "sender", str)
        state = get_json_request_value(value, 'state', dict)

        if sender == 'on_end' and not state['error']:
            punits_requests = kvdb.get(user_id + '__' + job_id)
            # punits_requests = get_json_request_value(punits_requests, 'punits', value_type=dict)
            subtract_processing_units(user_id=user_id, punits_request=punits_requests['progress'][0]['message'])

        return res
    except TimeoutError as e:
        raise api.ApiError(401, e.strerror)


def delete_callback(user_id: str, job_id: str):
    try:
        kv = KeyValueDatabase.instance()
        res = kv.delete(user_id + '__' + job_id)

        if res == 0:
            raise api.ApiError(404, 'Callback not found')
        elif res is None:
            raise api.ApiError(401, 'Deletion error')

        return res
    except TimeoutError as r:
        raise api.ApiError(401, r.strerror)