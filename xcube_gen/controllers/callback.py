from xcube_gen import api
from xcube_gen.api import get_json_request_value
from xcube_gen.keyvaluedatabase import KeyValueDatabase

from xcube_gen.controllers.users import subtract_processing_units
from xcube_gen.typedefs import JsonObject, AnyDict


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
        raise api.ApiError(401, 'Callbacks need a "message" as well as a "status"')

    try:
        kvdb = KeyValueDatabase.instance()
        kv = kvdb.get(user_id + '__' + job_id)
        if kv and 'progress' in kv:
            kv['progress'].append(value)
        if kv and 'progress' not in kv:
            kv['progress'] = [value]
        else:
            kv = dict(progress=[value])

        res = kvdb.set(user_id + '__' + job_id, kv)

        event = get_json_request_value(value, "sender", str)
        state = get_json_request_value(value, 'state', dict)

        # if 'exc_info' in state:
        #     exc_info = get_json_request_value(state, 'exc_info', tuple)
        #     raise api.ApiError(400, exc_info)

        if event == 'on_end' and not state['error']:
            punits_requests = kvdb.get(job_id)
            subtract_processing_units(user_id=user_id, punits_request=punits_requests)

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
