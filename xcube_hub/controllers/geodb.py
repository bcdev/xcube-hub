import os
from typing import Dict

import requests
from requests import HTTPError

from xcube_hub import api
from xcube_hub.auth0 import AUTH0_DOMAIN
from xcube_hub.typedefs import JsonObject


def geodb_auth_login_app():
    try:
        client_id = os.environ.get("XCUBE_GEODB_AUTH_CLIENT_ID", None)
    except ValueError:
        raise api.ApiError(400, "Error: XCUBE_GEODB_AUTH_CLIENT_ID must be set")

    try:
        client_secret = os.environ.get("XCUBE_GEODB_AUTH_CLIENT_SECRET", None)
    except ValueError:
        raise api.ApiError(400, "Error: XCUBE_GEODB_AUTH_CLIENT_SECRET must be set.")

    return {"client_id": client_id, "client-secret": client_secret}


def register_user(token: str, payload: Dict) -> bool:
    headers = {'Authorization': f"Bearer {token}", }

    if 'user_id' not in payload:
        raise api.ApiError(400, "Registering a user needs a user_id")

    if 'email' not in payload:
        raise api.ApiError(400, "Registering a user needs an email")

    try:
        url = f"https://{AUTH0_DOMAIN}/api/v2/users"
        res = requests.post(url=url, headers=headers, json=payload)
        res.raise_for_status()
    except HTTPError as e:
        raise api.ApiError(e.errno, str(e))
    except UnicodeError as e:
        raise api.ApiError(400, str(e))

    return True


def delete_user(token: str, user_id: str) -> bool:
    headers = {'Authorization': f"Bearer {token}", }

    if not user_id:
        raise api.ApiError(400, "Deleting a user needs a user_id")

    try:
        url = f"https://{AUTH0_DOMAIN}/api/v2/users/{user_id}"
        res = requests.delete(url=url, headers=headers)
        res.raise_for_status()
    except HTTPError as e:
        raise api.ApiError(e.errno, str(e))
    except UnicodeError as e:
        raise api.ApiError(400, str(e))

    return True


def get_user(token: str, user_id: str) -> JsonObject:
    headers = {'Authorization': f"Bearer {token}", }

    if not user_id:
        raise api.ApiError(400, "Deleting a user needs a user_id")

    try:
        url = f"https://{AUTH0_DOMAIN}/api/v2/users/{user_id}"
        res = requests.get(url=url, headers=headers)
        res.raise_for_status()
        return res.json()
    except HTTPError as e:
        raise api.ApiError(e.errno, str(e))
    except UnicodeError as e:
        raise api.ApiError(400, str(e))

