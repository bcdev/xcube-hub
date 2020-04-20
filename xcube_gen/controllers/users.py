import datetime
from typing import Optional

from xcube_gen.database import Database
from xcube_gen.types import AnyDict


def get_user_data(user_name: str) -> Optional[AnyDict]:
    return Database.instance().get_user_data(user_name)


def put_user_data(user_name: str, user_data: AnyDict):
    Database.instance().put_user_data(user_name, user_data)


def delete_user_data(user_name: str):
    Database.instance().delete_user_data(user_name)


def add_processing_units(user_name: str, processing_units: int):
    user_data = get_user_data(user_name) or dict()
    now = datetime.datetime.now()
    processing_units_total_old = user_data.get('processing_units_total', 0)
    processing_units_history_old = user_data.get('processing_units_history', [])
    processing_units_total_new = processing_units_total_old + processing_units
    user_data['processing_units_total'] = processing_units_total_new
    user_data['processing_units_history'] = [[now.strftime("%Y-%m-%d %H:%M:%S"), processing_units]] \
                                            + processing_units_history_old
    put_user_data(user_name, user_data)
