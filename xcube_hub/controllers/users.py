import connexion
import requests

from xcube_hub import api
from xcube_hub.models.api_user_response import ApiUserResponse  # noqa: E501
from xcube_hub.models.api_users_response import ApiUsersResponse  # noqa: E501
from xcube_hub.models.user import User  # noqa: E501


def add_user(user_id, user=None):  # noqa: E501
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

        user = User.from_dict(connexion.request.get_json())  # noqa: E501
        headers = {'Authorization': token}

        user = user.to_update_request()
        # created at and updated at not allowed in request
        r = requests.post('https://edc.eu.auth0.com/api/v2/users', json=user, headers=headers)

        if r.status_code < 200 or r.status_code >= 300:
            raise api.ApiError(400, r.json())

        return get_user_by_user_id(user_id=user_id)
    except api.ApiError as e:
        return e.response


def delete_user_by_user_id(user_id):  # noqa: E501
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


def get_user_by_user_id(user_id):  # noqa: E501
    """Get users

    Get user info  # noqa: E501

    :param user_id: User ID
    :type user_id: str

    :rtype: ApiUserResponse
    """

    try:
        token = connexion.request.headers["Authorization"]
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


def get_users():  # noqa: E501
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


def update_user_by_user_id(user_id, body=None):  # noqa: E501
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

        user = User.from_dict(connexion.request.get_json())  # noqa: E501
        headers = {'Authorization': f"Bearer {token}"}

        user = user.to_update_request()
        # created at and updated at not allowed in request

        r = requests.patch(f'https://edc.eu.auth0.com/api/v2/users/{user_id}', json=user, headers=headers)

        if r.status_code < 200 or r.status_code >= 300:
            raise api.ApiError(400, r.json())

        return get_user_by_user_id(user_id)
    except api.ApiError as e:
        return e.response
