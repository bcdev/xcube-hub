# The MIT License (MIT)
# Copyright (c) 2020 by the xcube development team and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
from typing import Dict
import requests
from requests import HTTPError
from xcube_hub_old import api
from xcube_hub_old.auth0 import AUTH0_DOMAIN
from xcube_hub_old.typedefs import JsonObject


def auth_login_app():
    try:
        client_id = os.environ.get("AUTH_CLIENT_ID", None)
    except ValueError:
        raise api.ApiError(400, "Error: AUTH_CLIENT_ID must be set")

    try:
        client_secret = os.environ.get("AUTH_CLIENT_SECRET", None)
    except ValueError:
        raise api.ApiError(400, "Error: AUTH_CLIENT_SECRET must be set.")

    return {"client_id": client_id, "client-secret": client_secret}


# noinspection PyUnboundLocalVariable
def register_user(token: str, payload: Dict) -> bool:
    headers = {'Authorization': f"Bearer {token}",  "Content-Type": "application/json" }

    if not isinstance(payload, Dict):
        raise api.ApiError(400, "Payload needs to be a dict.")

    if 'user_id' not in payload:
        raise api.ApiError(400, "Registering a user needs a user_id")

    if 'email' not in payload:
        raise api.ApiError(400, "Registering a user needs an email")

    try:
        url = f"https://{AUTH0_DOMAIN}/api/v2/users"
        res = requests.post(url=url, headers=headers, json=payload)
        res.raise_for_status()
    except HTTPError as e:
        raise api.ApiError(e.errno, str(e) + ': ' + res.text)
    except BaseException as e:
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
        # noinspection PyUnboundLocalVariable
        raise api.ApiError(e.errno, str(e) + ': ' + res.text)
    except BaseException as e:
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
        # noinspection PyUnboundLocalVariable
        raise api.ApiError(e.errno, str(e) + ': ' + res.text)
    except BaseException as e:
        raise api.ApiError(400, str(e))


def add_user_to_role(token: str, user_id: str, role_id: str):
    payload = {
        "users": [
            user_id,
        ],
    }

    headers = {'Authorization': f"Bearer {token}", }

    if not user_id:
        raise api.ApiError(400, "Allocating role to a user needs a user_id")

    if not role_id:
        raise api.ApiError(400, "Allocating role to a user needs a role_id")

    try:
        url = f"https://{AUTH0_DOMAIN}/api/v2/roles/{role_id}/users"
        res = requests.post(url=url, json=payload, headers=headers)
        res.raise_for_status()
        return res.json()
    except HTTPError as e:
        # noinspection PyUnboundLocalVariable
        raise api.ApiError(e.errno, str(e) + ': ' + res.text)
    except BaseException as e:
        raise api.ApiError(400, str(e))
