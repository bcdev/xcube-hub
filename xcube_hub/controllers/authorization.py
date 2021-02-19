import hashlib
import os
from typing import Dict

import connexion
from jose import jwt, ExpiredSignatureError, JWTError
from jose.exceptions import JWKError
from jwt import InvalidAlgorithmError
from werkzeug.exceptions import Forbidden, HTTPException

from xcube_hub import api
from xcube_hub.auth0 import verify_token

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


def get_aud(token: str) -> str:
    unverified_claims = jwt.get_unverified_claims(token)
    aud = unverified_claims.get("aud")

    if aud is None:
        raise api.ApiError(403, "access denied: No email.")

    return aud


def get_issuer(token: str):
    unverified_claims = jwt.get_unverified_claims(token)
    iss = unverified_claims.get("iss")

    if iss is None:
        raise api.ApiError(403, "access denied: No email.")

    return iss


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


def verify_local_token(token: str, audience: str):
    try:
        secret = _maybe_raise_for_env("XCUBE_HUB_TOKEN_SECRET")
        return jwt.decode(token, secret, audience=audience)
    except (JWKError, JWTError, InvalidAlgorithmError, ExpiredSignatureError) as e:
        raise Forbidden(description=str(e))


# noinspection PyPep8Naming
def check_oAuthorization(token):
    aud = _maybe_raise_for_env("XCUBE_HUB_OAUTH_AUD")
    iss = get_issuer(token=token)
    tgt_aud = get_aud(token=token)
    if iss == "https://xcube-gen.brockmann-consult.de/":
        claims = verify_local_token(token=token, audience=aud)
    elif iss == "https://edc.eu.auth0.com/":
        aud_um = _maybe_raise_for_env("XCUBE_HUB_OAUTH_USER_MANAGEMENT_AUD")
        if tgt_aud == aud_um:
            aud = aud_um

        claims = verify_token(token=token, audience=aud)
    else:
        raise api.ApiError(401, "Access denied. Issuer unknown.")

    permissions = get_permissions(claims=claims)
    return {'scopes': permissions}


# noinspection PyPep8Naming
def validate_scope_oAuthorization(required_scopes, token_scopes):
    return set(required_scopes).issubset(set(token_scopes))


