import secrets
import uuid
from datetime import datetime
from typing import Optional

import connexion
import requests

from xcube_hub import api
from xcube_hub.core import users
from xcube_hub.models.user import User


def get_request_body_from_user(user: User):
    res = user.to_dict()
    for k, v in res.items():
        res[k] = v.isoformat() if isinstance(v, datetime) else v

    return {k: v for k, v in res.items() if v is not None}


def _create_secret(secrets_length: int = 32):
    client_id = uuid.uuid4().hex
    client_secret = secrets.token_urlsafe(secrets_length)
    return client_id, client_secret


def add_user(user_id, user):
    """Add user

    Add user

    :param user_id: User ID
    :type user_id: str
    :param user: User information
    :type user: dict | bytes

    :rtype: ApiUserResponse
    """

    try:
        token = connexion.request.headers["Authorization"]

        user = User.from_dict(connexion.request.get_json())

        user_dict = users.supplement_user(user_id=user_id, user=user)

        headers = {'Authorization': token}

        # created at and updated at not allowed in request
        r = requests.post('https://edc.eu.auth0.com/api/v2/users', json=user_dict, headers=headers)

        if r.status_code < 200 or r.status_code >= 300:
            raise api.ApiError(400, r.json())

        users.assign_role_to_user(user_name=user_id, role_id="rol_UV2cTM5brIezM6i6")

        return get_user_by_user_id(user_id=user_id)
    except api.ApiError as e:
        return e.response


def delete_user_by_user_id(user_id):
    """Delete user

    Remove user from a service  # noqa: E501

    :param user_id: User ID
    :type user_id: str

    :rtype: None
    """
    try:
        token = connexion.request.headers["Authorization"]
        headers = {'Authorization': f"Bearer {token}"}

        r = requests.delete(f'https://edc.eu.auth0.com/api/v2/users/{user_id}', headers=headers)

        if r.status_code == 404:
            raise api.ApiError(404, f"User {user_id} not found.")

        if r.status_code < 200 or r.status_code >= 300:
            raise api.ApiError(400, r.json())

        return api.ApiResponse.success(result='Success')
    except api.ApiError as e:
        return e.response


def get_user_by_user_id(user_id: str, token: Optional[str] = None):
    """Get users

    Get user info  # noqa: E501

    :param user_id: User ID
    :type user_id: str
    :param token: Optional token
    :type token: Optional[str]

    :rtype: ApiUserResponse
    """

    try:
        token = token or connexion.request.headers["Authorization"]
        headers = {'Authorization': f"Bearer {token}"}

        r = requests.get(f'https://edc.eu.auth0.com/api/v2/users/{user_id}', headers=headers)

        if r.status_code == 404:
            raise api.ApiError(404, f"User {user_id} not found.")
        if r.status_code < 200 or r.status_code >= 300:
            raise api.ApiError(400, r.json())

        res = r.json()

        user = User.from_dict(res)
        if 'identities' in res and len(res['identities']) > 0:
            user.connection = res['identities'][0]['connection']

        return api.ApiResponse.success(result=user)
    except api.ApiError as e:
        return e.response


def get_users():
    """Get all users by service name

    Get all users by service name  # noqa: E501


    :rtype: ApiUsersResponse
    """
    try:
        token = connexion.request.headers["Authorization"]
        headers = {'Authorization': f"Bearer {token}"}

        r = requests.get('https://edc.eu.auth0.com/api/v2/users', headers=headers)

        if r.status_code < 200 or r.status_code >= 300:
            raise api.ApiError(400, r.json())

        res = r.json()
        if len(res) == 0:
            raise api.ApiError(404, f"No users not found.")

        return api.ApiResponse.success(result=res)
    except api.ApiError as e:
        return e.response


def update_user_by_user_id(user_id, body=None):
    """Update user

    List users in a service  # noqa: E501

    :param user_id: User ID
    :type user_id: str
    :param body: User information
    :type body: dict | bytes

    :rtype: ApiUserResponse
    """
    try:
        token = connexion.request.headers["Authorization"]

        user = User.from_dict(body)
        headers = {'Authorization': f"Bearer {token}"}

        user = get_request_body_from_user(user=user)
        # created at and updated at not allowed in request

        r = requests.patch(f'https://edc.eu.auth0.com/api/v2/users/{user_id}', json=user, headers=headers)

        if r.status_code == 404:
            raise api.ApiError(404, "User not found.")
        if r.status_code < 200 or r.status_code >= 300:
            raise api.ApiError(400, r.json())

        return get_user_by_user_id(user_id)
    except api.ApiError as e:
        return e.response


def update_secrets_by_user_id(user_id: str):
    try:
        token = connexion.request.headers["Authorization"]

        headers = {'Authorization': f"Bearer {token}"}
        user = get_user_by_user_id(user_id=user_id, token=token)
        user = user['result']

        user_metadata = user.user_metadata or {}

        client_id, client_secret = _create_secret()
        user_metadata.client_id = client_id
        user_metadata.client_secret = client_secret
        body = {"user_metadata": user_metadata.to_dict()}

        r = requests.patch(f'https://edc.eu.auth0.com/api/v2/users/{user_id}', json=body, headers=headers)

        if r.status_code == 404:
            raise api.ApiError(404, "User not found.")
        if r.status_code < 200 or r.status_code >= 300:
            raise api.ApiError(400, r.json())

        return get_user_by_user_id(user_id)
    except api.ApiError as e:
        return e.response


def delete_secrets_by_user_id(user_id: str):
    try:
        token = connexion.request.headers["Authorization"]

        headers = {'Authorization': f"Bearer {token}"}

        user = get_user_by_user_id(user_id=user_id, token=token)
        user = user['result']

        user_metadata = user.user_metadata or {}

        user_metadata.client_id = None
        user_metadata.client_secret = None
        body = {"user_metadata": user_metadata.to_dict()}

        r = requests.patch(f'https://edc.eu.auth0.com/api/v2/users/{user_id}', json=body, headers=headers)

        if r.status_code == 404:
            raise api.ApiError(404, "User not found.")
        if r.status_code < 200 or r.status_code >= 300:
            raise api.ApiError(400, r.json())

        return get_user_by_user_id(user_id)
    except api.ApiError as e:
        return e.response
