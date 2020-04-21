import datetime
from typing import Optional

from xcube_gen.api import ApiError, get_json_request_value
from xcube_gen.database import Database
from xcube_gen.types import JsonObject


def update_processing_units(user_name: str, processing_units: JsonObject, factor: int = 1):
    update_count = get_json_request_value(processing_units, 'count', value_type=int)
    if update_count <= 0:
        raise ApiError(400, 'Processing unit counts must be greater than zero')
    update_count *= factor
    user_data = get_user_data(user_name) or dict()
    now = datetime.datetime.now()
    processing_units = user_data.get('processingUnits', dict())
    count = processing_units.get('count', 0)
    history = processing_units.get('history', [])
    processing_units['count'] = count + update_count
    processing_units['history'] = [[now.strftime("%Y-%m-%d %H:%M:%S"), update_count]] + history
    user_data['processingUnits'] = processing_units
    put_user_data(user_name, user_data)


def get_user_data(user_name: str) -> Optional[JsonObject]:
    return Database.instance().get_user_data(user_name)


def put_user_data(user_name: str, user_data: JsonObject):
    Database.instance().put_user_data(user_name, user_data)


def delete_user_data(user_name: str):
    Database.instance().delete_user_data(user_name)
