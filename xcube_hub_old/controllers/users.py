import datetime
from typing import Optional, Sequence

import requests

from xcube_hub_old import auth0
from xcube_hub_old.api import ApiError, get_json_request_value
from xcube_hub_old.database import Database
from xcube_hub_old.typedefs import JsonObject


def get_processing_units(user_id: str, include_history: bool = False) -> JsonObject:
    processing_units = Database.instance().get_user_data(user_id, dataset_name='punits')
    if processing_units is not None and not include_history and 'history' in processing_units:
        processing_units.pop('history')
    return processing_units


def add_processing_units(user_id: str, punits_request: JsonObject):
    _update_processing_units(user_id, punits_request, 'add')


def subtract_processing_units(user_id: str, punits_request: JsonObject):
    _update_processing_units(user_id, punits_request, 'sub')


def _update_processing_units(user_id: str, punits_request: JsonObject, op: str):
    update_punits = get_json_request_value(punits_request, 'punits', value_type=dict)
    update_count = get_json_request_value(update_punits, 'total_count', value_type=int)
    if update_count <= 0:
        raise ApiError(400, 'Processing unit counts must be greater than zero.')
    punits_data_old = get_user_data(user_id, dataset_name='punits') or dict()
    count_old = punits_data_old.get('count', 0)
    history_old = punits_data_old.get('history', [])
    count_new = (count_old + update_count) if op == 'add' else (count_old - update_count)
    if count_new < 0:
        raise ApiError(400, 'Out of processing units.')
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


def get_users(token: str) -> Sequence[JsonObject]:
    import requests
    headers = {'Authorization': f'Bearer {token}'}
    res = requests.get("https://edc.eu.auth0.com/api/v2/users", headers=headers)
    res.raise_for_status()
    return res.json()


def get_role(user_id: str, token: str):
    import requests
    headers = {'Authorization': f'Bearer {token}'}
    res = requests.get(f"https://edc.eu.auth0.com/api/v2/users/{user_id}/roles", headers=headers)
    res.raise_for_status()
    return res.json()


def add_user(user_id: str, given_name: str, family_name: str, name: str, nickname: str, password: str, email: str):
    token = auth0.get_management_token()
    payload = {
        "email": email,
        "user_metadata": {},
        "blocked": False,
        "email_verified": True,
        "app_metadata": {
            "geodb_role": f"geodb_{user_id}"
        },
        "given_name": given_name,
        "family_name": family_name,
        "name": name,
        "nickname": nickname,
        "username": "geodb_{user_id}",
        "user_id": user_id,
        "connection": "Username-Password-Authentication",
        "password": password,
        "verify_email": False,
    }

    headers = {'Authorization': f"Bearer {token}"}

    requests.post('https://edc.eu.auth0.com/api/v2/users', payload=payload, headers=headers)


def assign_role_to_user(user_id: str, role_id: str):
    token = auth0.get_management_token()
    payload = {
        "roles": [
            f"auth0|{user_id}"
        ]
    }
    headers = {'Authorization': f"Bearer {token}"}
    requests.post(f'https://edc.eu.auth0.com/api/v2/roles/{role_id}/users', payload=payload, headers=headers)


def register_user_to_geodb(user_id: str, start_date: str, subscription_name: str, cells: int = 1000000):
    token = auth0.get_management_token()

    payload = [{
        "user_name": f"geodb_{user_id}",
        "start_date": start_date,
        "subscription": subscription_name,
        "cells": cells
    }]

    headers = {'Authorization': f"Bearer {token}"}

    requests.post('https://xcube-geodb.brockmann-consult.de/geodb_user_info', payload=payload, headers=headers)


