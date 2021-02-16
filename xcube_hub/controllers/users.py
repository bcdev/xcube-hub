from typing import Optional, Sequence

import connexion
import requests

from xcube_hub import api
from xcube_hub.controllers import punits
from xcube_hub.models.user import User  # noqa: E501


def get_request_body_from_user(user: User):
    res = user.to_dict()

    return {k: v for k, v in res.items() if v is not None}


def add_user(user_id, user):
    """Add user

    Add user  # noqa: E501

    :param user_id: User ID
    :type user_id: str
    :param user: User information
    :type user: dict | bytes

    :rtype: ApiUserResponse
    """

    if not connexion.request.is_json:
        raise api.ApiError(400, "System error: body is not of type json.")

    try:
        token = connexion.request.headers["Authorization"]

        user = User.from_dict(user)

        punits.add_punits(user_id=user_id, punits_request={})

        headers = {'Authorization': token}

        user = get_request_body_from_user(user)
        # created at and updated at not allowed in request
        r = requests.post('https://edc.eu.auth0.com/api/v2/users', json=user, headers=headers)

        if r.status_code < 200 or r.status_code >= 300:
            raise api.ApiError(400, r.json())

        assign_role_to_user(user_name=user_id, role_id="rol_UV2cTM5brIezM6i6")

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
    if not connexion.request.is_json:
        raise api.ApiError(400, "System error: body is not of type json.")

    try:
        token = connexion.request.headers["Authorization"]

        user = User.from_dict(body)
        headers = {'Authorization': f"Bearer {token}"}

        user = get_request_body_from_user(user=user)
        # created at and updated at not allowed in request

        r = requests.patch(f'https://edc.eu.auth0.com/api/v2/users/{user_id}', json=user, headers=headers)

        if r.status_code < 200 or r.status_code >= 300:
            raise api.ApiError(400, r.json())

        return get_user_by_user_id(user_id)
    except api.ApiError as e:
        return e.response


def assign_role_to_user(user_name: str, role_id: str, token: Optional[str] = None):
    token = token or connexion.request.headers["Authorization"]
    payload = {
        "roles": [
            f"auth0|{user_name}"
        ]
    }
    headers = {'Authorization': f"Bearer {token}"}
    requests.post(f'https://edc.eu.auth0.com/api/v2/roles/{role_id}/users', payload=payload, headers=headers)


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
