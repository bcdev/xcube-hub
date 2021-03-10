import datetime
import os
from typing import Dict, Optional
from urllib.error import HTTPError

import requests
from jose import jwt
from werkzeug.exceptions import Unauthorized

from xcube_hub import api
from xcube_hub.core import users, oauth
from xcube_hub.models.oauth_token import OauthToken
from xcube_hub.models.user import User
from xcube_hub.util import maybe_raise_for_env


def _get_management_token(client_id: Optional[str] = None, client_secret: Optional[str] = None):
    client_id = client_id or os.environ.get("AUTH0_USER_MANAGEMENT_CLIENT_ID", None)
    if client_id is None:
        raise Unauthorized(description="Please configure the env variable AUTH0_USER_MANAGEMENT_CLIENT_ID")

    client_secret = client_secret or os.environ.get("AUTH0_USER_MANAGEMENT_CLIENT_SECRET", None)
    if client_secret is None:
        raise Unauthorized(description="Please configure the env variable AUTH0_USER_MANAGEMENT_CLIENT_SECRET")

    audience = os.getenv("XCUBE_HUB_OAUTH_USER_MANAGEMENT_AUD", None)
    if audience is None:
        raise api.ApiError(401, "Unauthorized. System needs XCUBE_HUB_OAUTH_USER_MANAGEMENT_AUD")

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": audience,
        "grant_type": "client_credentials"
    }

    res = requests.post("https://edc.eu.auth0.com/oauth/token", json=payload)

    try:
        res.raise_for_status()
    except HTTPError as e:
        raise Unauthorized(description=str(e))

    try:
        return res.json()["access_token"]
    except KeyError:
        raise Unauthorized(description="System error: Could not find key 'access_token' in auth0's response")


def create_token(claims: Dict, days_valid: int = 90):
    secret = maybe_raise_for_env("XCUBE_HUB_TOKEN_SECRET")

    if len(secret) < 256:
        raise api.ApiError(400, "System Error: Invalid token secret given.")

    exp = datetime.datetime.utcnow() + datetime.timedelta(days=days_valid)

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

        aud = maybe_raise_for_env("XCUBE_HUB_OAUTH_AUD")
        oauth_token = OauthToken.from_dict(body)
        token = _get_management_token()
        res = oauth.get_user_by_credentials(token=token,
                                            client_id=oauth_token.client_id,
                                            client_secret=oauth_token.client_secret)

        user = User.from_dict(res[0])
        permissions = users.get_permissions_by_user_id(user.user_id, token=token)
        permissions = users.get_permissions(permissions=permissions)
        claims = {
            "iss": "https://xcube-gen.brockmann-consult.de/",
            "aud": [aud],
            "scope": " ".join(permissions),
            "gty": "client-credentials",
            "email": user.email,
            "permissions": permissions
        }

        if user.app_metadata and user.app_metadata.geodb_role:
            claims["https://geodb.brockmann-consult.de/dbrole"] = user.app_metadata.geodb_role

        encoded_jwt = create_token(claims)

        return dict(access_token=encoded_jwt, token_type="bearer")
    except api.ApiError as e:
        return e.response
