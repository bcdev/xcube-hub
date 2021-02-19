from typing import Sequence

import requests

from xcube_hub import api


def get_user_by_credentials(token: str, client_id: str, client_secret: str) -> Sequence:
    q = f'(user_metadata.client_id: "{client_id}") AND (user_metadata.client_secret: "{client_secret}")'
    headers = {'Authorization': f"Bearer {token}"}

    r = requests.get('https://edc.eu.auth0.com/api/v2/users', params={'q': q}, headers=headers)

    if r.status_code < 200 or r.status_code >= 300:
        raise api.ApiError(400, r.json())

    res = r.json()
    if len(res) == 0:
        raise api.ApiError(404, f"No users not found.")
    if len(res) > 1:
        raise api.ApiError(400, f"More than one user found.")

    return res

