from datetime import datetime
from typing import Optional, Sequence

import connexion
import requests

from xcube_hub import api, util
from xcube_hub.models.subscription import Subscription
from xcube_hub.models.user import User
from xcube_hub.util import create_user_id_from_email, create_secret


def get_permissions_by_user_id(auth_user_id: str, token: Optional[str] = None):
    token = token or connexion.request.headers["Authorization"]

    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(f"https://edc.eu.auth0.com/api/v2/users/{auth_user_id}/permissions", headers=headers)

    if r.status_code == 404:
        raise api.ApiError(404, "User not found.")
    if r.status_code < 200 or r.status_code >= 300:
        raise api.ApiError(400, r.text)

    return r.json()


def get_permissions(permissions: Sequence) -> Sequence:
    permissions_names = []
    for permission in permissions:
        permissions_names.append(permission['permission_name'])

    return permissions_names


def get_request_body_from_user(user: User):
    res = user.to_dict()
    for k, v in res.items():
        res[k] = v.isoformat() if isinstance(v, datetime) else v

    return {k: v for k, v in res.items() if v is not None}


def supplement_user(user: User, subscription: Subscription):
    user.user_id = create_user_id_from_email(user.email)

    client_id, client_secret = create_secret()
    user.user_metadata.client_id = subscription.client_id or client_id
    user.user_metadata.client_secret = subscription.client_secret or client_secret
    user.password = util.generate_temp_password()

    return user
