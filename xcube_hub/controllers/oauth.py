from typing import Sequence

import connexion
import requests
from jose import jwt

from xcube_hub import auth0, api
from xcube_hub.controllers import users
from xcube_hub.models.oauth_token import OauthToken
from xcube_hub.models.user import User


def get_user_by_credentials(token: str, client_id: str, client_secret: str) -> Sequence:
    q = f'(app_metadata.client_id: "{client_id}") AND (app_metadata.client_secret: "{client_secret}")'
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


def oauth_token_post(body: OauthToken):
    """Get authorization token

    Get authorization token

    :param body: OauthToken
    :type body: dict | bytes

    :rtype: ApiOAuthResponse
    """
    if connexion.request.is_json:
        try:
            oauth_token = OauthToken.from_dict(body)
            token = auth0.get_management_token()
            res = get_user_by_credentials(token=token,
                                          client_id=oauth_token.client_id,
                                          client_secret=oauth_token.client_secret)

            user = User.from_dict(res[0])
            permissions = users.get_permissions_by_user_id(user.user_id, token=token)
            permissions = users.get_permissions(permissions=permissions)
            claims = {
                "iss": "https://edc.eu.auth0.com/",
                "aud": "https://xcube-gen.brockmann-consult.de/api/v1/",
                "azp": "13eBlDZ6a4pQr5oY9gm26YZ1coRZTs3J",
                "scope": permissions,
                "gty": "client-credentials",
                "email": user.email,
                "permissions": permissions
            }

            # TODO: Make secret secret
            encoded_jwt = jwt.encode(claims, "", algorithm="HS256")

            return dict(access_token=encoded_jwt, token_type="bearer")
        except api.ApiError as e:
            return e.response
