import hashlib
import os
from typing import Dict

import connexion
from jose import jwt, ExpiredSignatureError, JWTError
from jwt import InvalidAlgorithmError
from werkzeug.exceptions import Forbidden, HTTPException

from xcube_hub import api


"""
controller generated to handled auth operation described at:
https://connexion.readthedocs.io/en/latest/security.html
"""


def get_email(token: str) -> str:
    unverified_claims = jwt.get_unverified_claims(token)
    email = unverified_claims.get("email")

    if email is None:
        raise api.ApiError(403, "access denied: No email.")

    return email


def get_permissions(claims: Dict):
    permissions = []
    if 'permissions' in claims:
        permissions = claims.get("permissions")
    elif 'scope' in claims:
        permissions = claims.get("scope").split(' ')

    if permissions is None:
        raise api.ApiError(403, "access denied: Insufficient permissions.")

    return permissions


# noinspection InsecureHash
def get_user_id() -> str:
    if 'Authorization' not in connexion.request.headers:
        raise api.ApiError(403, "Access denied.")

    token = connexion.request.headers["Authorization"]
    if "Bearer " in token:
        token = token.replace("Bearer ", "")

    email = get_email(token)

    res = hashlib.md5(email.encode())

    return 'a' + res.hexdigest()


class ApiEnvError(HTTPException):
    code = 500
    description = "System error. Env var {env_var} must be given."


def _maybe_raise_for_env(env_var: str):
    env = os.environ.get(env_var, None)
    if env is None:
        raise ApiEnvError(description=f"System error. Env var {env_var} must be given.")

    return env


# noinspection PyPep8Naming
def check_oAuthorization(token):
    try:
        secret = _maybe_raise_for_env("XCUBE_HUB_TOKEN_SECRET")
        aud = _maybe_raise_for_env("XCUBE_HUB_OAUTH_AUD")
        claims = jwt.decode(token, secret, audience=aud)
    except (JWTError, InvalidAlgorithmError, ExpiredSignatureError) as e:
        raise Forbidden(description=str(e))

    permissions = get_permissions(claims=claims)
    email = claims['email']
    return {'scopes': permissions, 'email': email}


# noinspection PyPep8Naming
def validate_scope_oAuthorization(required_scopes, token_scopes):
    return set(required_scopes).issubset(set(token_scopes))


