import datetime
from typing import Optional

from xcube_gen.api import ApiError
from xcube_gen.database import Database
from xcube_gen.types import AnyDict


def update_processing_units(user_name: str, op: str, delta_count: int):
    if op not in ('charge', 'consume'):
        raise ApiError(400, 'Processing unit operation must be either "charge" or "consume"')
    if delta_count < 0:
        raise ApiError(400, 'Processing unit counts must be greater than zero')
    if op == 'consume':
        delta_count *= -1
    user_data = get_user_data(user_name) or dict()
    now = datetime.datetime.now()
    processing_units = user_data.get('processingUnits', dict())
    count = processing_units.get('count', 0)
    history = processing_units.get('history', [])
    processing_units['count'] = count + delta_count
    processing_units['history'] = [[now.strftime("%Y-%m-%d %H:%M:%S"), delta_count]] + history
    user_data['processingUnits'] = processing_units
    put_user_data(user_name, user_data)


def get_user_data(user_name: str) -> Optional[AnyDict]:
    return Database.instance().get_user_data(user_name)


def put_user_data(user_name: str, user_data: AnyDict):
    Database.instance().put_user_data(user_name, user_data)


def delete_user_data(user_name: str):
    Database.instance().delete_user_data(user_name)
