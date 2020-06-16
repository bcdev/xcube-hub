import json
from xcube_gen import api
from xcube_gen.cache import Cache
from xcube_gen.events import PutEvents, GetEvents, DeleteEvents
from xcube_gen.xg_types import JsonObject, AnyDict


def get_callback(user_id: str, job_id: str) -> JsonObject:
    try:
        cache = Cache()
        res = cache.get(user_id + '__' + job_id)

        if res:
            res = json.loads(res)
        else:
            raise api.ApiError(404, 'Could not find any callback entries for that key.')

        GetEvents.finished(user_id=user_id, job_id=job_id)

        return res
    except TimeoutError as r:
        raise api.ApiError(401, r.strerror)


def put_callback(user_id: str, job_id: str, value: AnyDict):
    if not value or 'message' not in value or 'status' not in value:
        raise api.ApiError(401, 'Callbacks need a "message" as well as a "status"')

    try:
        cache = Cache()
        res = cache.set(user_id + '__' + job_id, json.dumps(value))
        PutEvents.finished(user_id=user_id, job_id=job_id, value=value)
        return res
    except TimeoutError as e:
        raise api.ApiError(401, e.strerror)


def delete_callback(user_id: str, job_id: str):
    try:
        cache = Cache()
        res = cache.delete(user_id + '__' + job_id)

        if res == 0:
            raise api.ApiError(404, 'Callback not found')
        elif res is None:
            raise api.ApiError(401, 'Deletion error')

        DeleteEvents.finished(user_id=user_id, job_id=job_id)

        return res
    except TimeoutError as r:
        raise api.ApiError(401, r.strerror)


