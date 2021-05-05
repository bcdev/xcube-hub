import datetime
from typing import Optional

from xcube_hub import api
from xcube_hub.api import get_json_request_value
from xcube_hub.database import Database
from xcube_hub.typedefs import JsonObject


def get_punits(user_id: str, include_history: bool = False) -> JsonObject:
    processing_units = Database.instance().get_user_data(user_id, dataset_name='punits')
    if processing_units is not None and not include_history and 'history' in processing_units:
        processing_units.pop('history')
    return processing_units


def add_punits(user_id: str, punits_request: JsonObject):
    _update_punits(user_id, punits_request, 'add')


def subtract_punits(user_id: str, punits_request: JsonObject):
    _update_punits(user_id, punits_request, 'sub')


def override_punits(user_id: str, punits_request: JsonObject):
    _update_punits(user_id, punits_request, 'override')


def _update_punits(user_id: str, punits_request: JsonObject, op: str):
    update_punits = get_json_request_value(punits_request, 'punits', value_type=dict)
    update_count = get_json_request_value(update_punits, 'total_count', value_type=int)
    if update_count <= 0:
        raise api.ApiError(400, 'Processing unit counts must be greater than zero.')
    punits_data_old = get_user_data(user_id, dataset_name='punits') or dict()
    count_old = punits_data_old.get('count', 0)
    history_old = punits_data_old.get('history', [])

    if op == 'add':
        count_new = (count_old + update_count)
    elif op == "sub":
        count_new = (count_old - update_count)
    else:
        count_new = update_count

    if count_new < 0:
        raise api.ApiError(400, 'Out of processing units.')
    history_new = [[datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), op, punits_request]] + history_old
    punits_data_new = dict(punits_data_old)
    punits_data_new['count'] = count_new
    punits_data_new['history'] = history_new
    put_user_data(user_id, punits_data_new, dataset_name='punits')


def get_user_data(user_id: str, dataset_name: str = 'data') -> Optional[JsonObject]:
    return Database.instance().get_user_data(user_id, dataset_name)


def put_user_data(user_id: str, user_data: JsonObject, dataset_name: str = 'data'):
    Database.instance().put_user_data(user_id, dataset_name, user_data)


def delete_user_data(user_id: str, dataset_name: str = 'data'):
    Database.instance().delete_user_data(user_id, dataset_name)
