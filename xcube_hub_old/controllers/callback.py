from xcube_hub_old import api
from xcube_hub_old.api import get_json_request_value
from xcube_hub_old.auth0 import Auth0
from xcube_hub_old.controllers.sizeandcost import get_size_and_cost
from xcube_hub_old.keyvaluedatabase import KeyValueDatabase

from xcube_hub_old.controllers.users import subtract_processing_units
from xcube_hub_old.typedefs import JsonObject, AnyDict


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
            processing_request = kvdb.get(user_id + '__' + job_id + '__cfg')
            punits_requests = get_size_and_cost(processing_request)

            token = Auth0.get_token_auth_header()
            user_info = Auth0.get_user_info_from_auth0(token, user_id)

            try:
                subtract_processing_units(user_id=user_info['name'], punits_request=punits_requests)
            except KeyError as e:
                raise api.ApiError(400, "System error: Could not substract processing units: " + str(e))

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
