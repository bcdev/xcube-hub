import secrets
import uuid
from datetime import datetime
from typing import Optional, Sequence

import connexion
import requests
from requests import HTTPError

from xcube_hub import api
from xcube_hub.core import punits
from xcube_hub.models.user import User
from xcube_hub.models.user_user_metadata import UserUserMetadata
from xcube_hub.util import strap_token


def assign_role_to_user(user_id: str, role_id: str, token: Optional[str] = None):
    token = token or strap_token()
    payload = {
        "roles": [
            f"{role_id}"
        ]
    }
    headers = {'Authorization': f"Bearer {token}"}
    r = requests.post(f'https://edc.eu.auth0.com/api/v2/users/auth0|{user_id}/roles', json=payload, headers=headers)

    if r.status_code == 404:
        raise api.ApiError(404, "Role not found.")
    if r.status_code < 200 or r.status_code >= 300:
        raise api.ApiError(400, r.json())


def get_permissions_by_user_id(auth_user_id: str, token: Optional[str] = None):
    token = token or connexion.request.headers["Authorization"]

    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(f"https://edc.eu.auth0.com/api/v2/users/{auth_user_id}/permissions", headers=headers)

    if r.status_code == 404:
        raise api.ApiError(404, "User not found.")
    if r.status_code < 200 or r.status_code >= 300:
        raise api.ApiError(400, r.json())

    return r.json()


def get_user_by_user_id(token: str, user_id: str) -> User:
    headers = {'Authorization': f"Bearer {token}"}

    r = requests.get('https://edc.eu.auth0.com/api/v2/users/auth0|' + user_id, headers=headers)

    try:
        r.raise_for_status()
    except HTTPError as e:
        raise api.ApiError(r.status_code, r.json())

    res = r.json()

    user = User.from_dict(res)

    if 'identities' in res and len(res['identities']) > 0:
        user.connection = res['identities'][0]['connection']

    return user


def get_permissions(permissions: Sequence) -> Sequence:
    permissions_names = []
    for permission in permissions:
        permissions_names.append(permission['permission_name'])

    return permissions_names


def _create_secret(secrets_length: int = 32):
    client_id = uuid.uuid4().hex
    client_secret = secrets.token_urlsafe(secrets_length)
    return client_id, client_secret


def _get_request_body_from_user(user: User):
    res = user.to_dict()
    for k, v in res.items():
        res[k] = v.isoformat() if isinstance(v, datetime) else v

    return {k: v for k, v in res.items() if v is not None}


def supplement_user(user_id: str, user: User):
    if user.user_metadata is None:
        user.user_metadata = UserUserMetadata()

    if user.user_metadata.punits is not None:
        punits.add_punits(user_id=user_id,
                          punits_request=dict(punits=dict(total_count=int(user.user_metadata.punits))))

    client_id, client_secret = _create_secret()
    user.user_metadata.client_id = client_id
    user.user_metadata.client_secret = client_secret
    user.user_metadata.xcube_user_id = user_id

    return _get_request_body_from_user(user=user)
