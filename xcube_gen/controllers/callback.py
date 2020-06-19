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


def trigger_punit_substract(user_id: str, value: AnyDict) -> None:
    status = get_json_request_value(value, 'status', value_type=str)

    if status == "CUBE_GENERATED":
        punits_requests = get_json_request_value(value, 'values', value_type=dict)
        subtract_processing_units(user_id=user_id, punits_request=punits_requests)


def put_callback(user_id: str, job_id: str, value: AnyDict):
    if 'message' not in value or 'status' not in value:
        raise api.ApiError(401, 'Callbacks need a "message" as well as a "status"')

    try:
        kvdb = KeyValueDatabase.instance()
        res = kvdb.set(user_id + '__' + job_id, value)
        trigger_punit_substract(user_id=user_id, value=value)
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
