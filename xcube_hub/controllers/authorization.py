import hashlib

import connexion
from jose import jwt, ExpiredSignatureError
from jwt import InvalidAlgorithmError

from xcube_hub import api
from xcube_hub.controllers.oauth import _maybe_raise_for_env

"""
controller generated to handled auth operation described at:
https://connexion.readthedocs.io/en/latest/security.html
"""


def get_permissions(token: str):
    unverified_claims = jwt.get_unverified_claims(token)
    permissions = []
    if 'permissions' in unverified_claims:
        permissions = unverified_claims.get("permissions")
    elif 'scope' in unverified_claims:
        permissions = unverified_claims.get("scope").split(' ')

    if permissions is None:
        raise api.ApiError(403, "access denied: Insufficient permissions.")

    return permissions


def get_aud(token: str):
    unverified_claims = jwt.get_unverified_claims(token)
    aud = unverified_claims.get("aud")

    if aud is None:
        raise api.ApiError(403, "access denied: No audience.")

    return aud


def get_email(token: str) -> str:
    unverified_claims = jwt.get_unverified_claims(token)
    email = unverified_claims.get("email")

    if email is None:
        raise api.ApiError(403, "access denied: No email.")

    return email


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


# noinspection PyPep8Naming
def check_oAuthorization(token):
    try:
        secret = _maybe_raise_for_env("XCUBE_HUB_TOKEN_SECRET")
        jwt.decode(token, secret)
    except (InvalidAlgorithmError, ExpiredSignatureError):
        return {'scopes': []}

    permissions = get_permissions(token=token)
    aud = get_aud(token=token)
    email = get_email(token=token)
    return {'scopes': permissions, 'aud': aud, 'email': email}


# noinspection PyPep8Naming
def validate_scope_oAuthorization(required_scopes, token_scopes):
    return set(required_scopes).issubset(set(token_scopes))


