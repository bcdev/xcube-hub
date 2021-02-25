from typing import Dict

import requests
from requests import HTTPError

from xcube_hub import api
from xcube_hub.core import users
from xcube_hub.models.user import User
from xcube_hub.models.user_user_metadata import UserUserMetadata
from xcube_hub.util import create_user_id_from_email, create_secret


_APP_TO_ROLE = {
    "xcube-gen": "rol_UV2cTM5brIezM6i6",
    "xcube-geodb": "rol_nF3PSuWkOJLk1mkm"
}


def put_user(user: Dict, token_info: Dict):
    try:
        user = User.from_dict(user)
        user.user_id = create_user_id_from_email(user.email)
        user = users.supplement_user(user=user)
        headers = {'Authorization': f"Bearer {token_info['token']}"}
        user_dict = users.get_request_body_from_user(user)

        r = requests.post("https://edc.eu.auth0.com/api/v2/users", json=user_dict, headers=headers)
        try:
            r.raise_for_status()
        except HTTPError as e:
            raise api.ApiError(r.status_code, str(e))
    except api.ApiError as e:
        return e.response


def patch_user(user_id: str, user: Dict, token_info: Dict):
    try:
        user = User.from_dict(user)
        headers = {'Authorization': f"Bearer {token_info['token']}"}
        user_dict = users.get_request_body_from_user(user)

        r = requests.patch(f"https://edc.eu.auth0.com/api/v2/users/auth0|{user_id}", json=user_dict, headers=headers)
        try:
            r.raise_for_status()
        except HTTPError as e:
            raise api.ApiError(r.status_code, str(e))
    except api.ApiError as e:
        return e.response


def patch_user_credentials(user_id: str, token_info: Dict):
    try:
        headers = {'Authorization': f"Bearer {token_info['token']}"}

        client_id, client_secret = create_secret()
        user_metadata = UserUserMetadata(client_id=client_id, client_secret=client_secret)

        r = requests.patch(f"https://edc.eu.auth0.com/api/v2/users/auth0|{user_id}",
                           json={'user_metadata': user_metadata.to_dict()},
                           headers=headers)

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise api.ApiError(r.status_code, str(e))
    except api.ApiError as e:
        return e.response


def put_user_to_app(user_id: str, app_id: str, token_info: Dict):
    try:
        if app_id not in _APP_TO_ROLE:
            raise api.ApiError(404, "App not found")

        role_id = _APP_TO_ROLE[app_id]
        users.assign_role_to_user(user_id=user_id, role_id=role_id, token=token_info['token'])
    except api.ApiError as e:
        return e.response


def delete_user_from_app(user_id: str, app_id: str, token_info: Dict):
    try:
        if app_id not in _APP_TO_ROLE:
            raise api.ApiError(404, "App not found")

        role_id = _APP_TO_ROLE[app_id]
        users.remove_role_from_user(user_id=user_id, role_id=role_id, token=token_info['token'])
    except api.ApiError as e:
        return e.response


def get_user_apps(user_id: str, token_info: Dict):
    try:
        headers = {'Authorization': f"Bearer {token_info['token']}"}
        r = requests.get(f"https://edc.eu.auth0.com/api/v2/users/auth0|{user_id}/roles", headers=headers)

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise api.ApiError(r.status_code, str(e))
        
        res = r.json()

        apps = [_APP_TO_ROLE[role['id']] for role in res if role['id'] in _APP_TO_ROLE]

        return api.ApiResponse.success(apps)
    except api.ApiError as e:
        return e.response
