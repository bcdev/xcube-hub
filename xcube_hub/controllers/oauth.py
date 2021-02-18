import datetime
import os
from typing import Dict

import connexion
from jose import jwt

from xcube_hub import auth0, api
from xcube_hub.core import users, oauth
from xcube_hub.models.oauth_token import OauthToken
from xcube_hub.models.user import User


def _maybe_raise_for_env(env_var: str):
    env = os.environ.get(env_var, None)
    if env is None:
        raise api.ApiError(400, f"Env var {env_var} must be set")

    return env


def _create_token(claims: Dict, days_valid: int = 90):
    secret = _maybe_raise_for_env("XCUBE_HUB_TOKEN_SECRET")

    if len(secret) < 256:
        raise api.ApiError(400, "System Error: Invalid token secret given.")

    exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)

    claims['exp'] = exp

    return jwt.encode(claims, secret, algorithm="HS256")


def oauth_token_post(body: OauthToken):
    """Get authorization token

    Get authorization token

    :param body: OauthToken
    :type body: dict | bytes

    :rtype: ApiOAuthResponse
    """

    try:
        if not connexion.request.is_json:
            raise api.ApiError(400, "System Error: Not a JSON request.")

        aud = _maybe_raise_for_env("XCUBE_HUB_OAUTH_AUD")

        oauth_token = OauthToken.from_dict(body)
        token = auth0.get_management_token()
        res = oauth.get_user_by_credentials(token=token,
                                            client_id=oauth_token.client_id,
                                            client_secret=oauth_token.client_secret)

        user = User.from_dict(res[0])
        permissions = users.get_permissions_by_user_id(user.user_id, token=token)
        permissions = users.get_permissions(permissions=permissions)
        claims = {
            "iss": "https://edc.eu.auth0.com/",
            "aud": aud,
            "scope": permissions,
            "gty": "client-credentials",
            "email": user.email,
            "permissions": permissions
        }

        encoded_jwt = _create_token(claims)

        return dict(access_token=encoded_jwt, token_type="bearer")
    except api.ApiError as e:
        return e.response
