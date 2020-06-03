import json

import redis

from xcube_gen import api
from xcube_gen.events import PUT_EVENTS
from xcube_gen.kv import Kv, KvError
from xcube_gen.xg_types import JsonObject, AnyDict


def get_callback(user_id: str, job_id: str) -> JsonObject:
    r = redis.Redis()
    try:
        res = r.get(user_id + '__' + job_id)
    except TimeoutError as r:
        raise api.ApiError(401, r.strerror)

    if res:
        return json.loads(res)
    else:
        raise api.ApiError(404, 'Could not find any callbacks')


def _put_finished(**kwargs):
    PUT_EVENTS.finished(**kwargs)


def put_callback(user_id: str, job_id: str, value: AnyDict, kv_provider: str):
    if 'message' not in value or 'status' not in value:
        raise api.ApiError(401, 'Callbacks need a "message" as well as a "status"')

    try:
        _db = Kv.instance(kv_provider=kv_provider)
    except KvError as e:
        raise api.ApiError(401, str(e))

    try:
        res = _db.set(user_id + '__' + job_id, json.dumps(value))
        _put_finished(user_id=user_id, job_id=job_id, value=value)
    except TimeoutError as e:
        raise api.ApiError(401, e.strerror)

    return res


def delete_callback(user_id: str, job_id: str):
    r = redis.Redis()

    try:
        res = r.delete(user_id + '__' + job_id)
    except TimeoutError as r:
        raise api.ApiError(401, r.strerror)

    if res == 0:
        raise api.ApiError(404, 'Callback not found')
    elif res is None:
        raise api.ApiError(401, 'Deletion error')

    return res
