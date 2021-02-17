import secrets
import uuid
from datetime import datetime
from typing import Optional, Sequence

import connexion
import requests

from xcube_hub.controllers import punits
from xcube_hub.models.user import User
from xcube_hub.models.user_user_metadata import UserUserMetadata


def assign_role_to_user(user_name: str, role_id: str, token: Optional[str] = None):
    token = token or connexion.request.headers["Authorization"]
    payload = {
        "roles": [
            f"auth0|{user_name}"
        ]
    }
    headers = {'Authorization': f"Bearer {token}"}
    requests.post(f'https://edc.eu.auth0.com/api/v2/roles/{role_id}/users', json=payload, headers=headers)


def get_role_by_user_id(user_id: str, token: str):
    import requests
    headers = {'Authorization': f'Bearer {token}'}
    res = requests.get(f"https://edc.eu.auth0.com/api/v2/users/{user_id}/roles", headers=headers)
    res.raise_for_status()
    return res.json()


def get_permissions_by_user_id(user_id: str, token: str):
    import requests
    headers = {'Authorization': f'Bearer {token}'}
    res = requests.get(f"https://edc.eu.auth0.com/api/v2/users/{user_id}/permissions", headers=headers)
    res.raise_for_status()
    return res.json()


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

    return _get_request_body_from_user(user=user)
