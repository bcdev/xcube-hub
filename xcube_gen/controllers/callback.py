import json
from xcube_gen import api
from xcube_gen.events import CALLBACK_PUT_EVENTS, CALLBACK_DELETE_EVENTS, CALLBACK_GET_EVENTS
from xcube_gen.cache import Cache
from xcube_gen.xg_types import JsonObject, AnyDict


def get_callback(user_id: str, job_id: str, kv: Cache) -> JsonObject:
    try:
        res = kv.get(user_id + '__' + job_id)
    except TimeoutError as r:
        raise api.ApiError(401, r.strerror)

    if res:
        res = json.loads(res)
    else:
        raise api.ApiError(404, 'Could not find any callback entries for that key.')

    CALLBACK_GET_EVENTS.finished(user_id=user_id, job_id=job_id)

    return res


def put_callback(user_id: str, job_id: str, value: AnyDict, kv: Cache):
    if 'message' not in value or 'status' not in value:
        raise api.ApiError(401, 'Callbacks need a "message" as well as a "status"')

    try:
        res = kv.set(user_id + '__' + job_id, json.dumps(value))
    except TimeoutError as e:
        raise api.ApiError(401, e.strerror)

    CALLBACK_PUT_EVENTS.finished(user_id=user_id, job_id=job_id, value=value)
    return res


def delete_callback(user_id: str, job_id: str, kv: Cache):
    try:
        res = kv.delete(user_id + '__' + job_id)
    except TimeoutError as r:
        raise api.ApiError(401, r.strerror)

    if res == 0:
        raise api.ApiError(404, 'Callback not found')
    elif res is None:
        raise api.ApiError(401, 'Deletion error')

    CALLBACK_DELETE_EVENTS.finished(user_id=user_id, job_id=job_id)

    return res
