from typing import Optional, Sequence

import connexion
import requests


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
