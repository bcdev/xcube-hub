import datetime
from typing import Dict

from jose import jwt

from xcube_hub import api
from xcube_hub.auth import Auth
from xcube_hub.core import users, oauth
from xcube_hub.models.oauth_token import OauthToken
from xcube_hub.models.user import User
from xcube_hub.util import maybe_raise_for_env


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
        auth = Auth.instance()
        aud = maybe_raise_for_env("XCUBE_HUB_OAUTH_AUD")

        oauth_token = OauthToken.from_dict(body)
        token = auth.get_management_token()
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

        encoded_jwt = create_token(claims)

        return dict(access_token=encoded_jwt, token_type="bearer")
    except api.ApiError as e:
        return e.response
