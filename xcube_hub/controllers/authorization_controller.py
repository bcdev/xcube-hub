from jose import jwt

from xcube_hub import api


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


# noinspection PyPep8Naming
def check_oAuthorization(token):
    permissions = get_permissions(token=token)
    aud = get_aud(token=token)
    return {'scopes': permissions, 'aud': aud, 'uid': 'test_value'}


# noinspection PyPep8Naming
def validate_scope_oAuthorization(required_scopes, token_scopes):
    return set(required_scopes).issubset(set(token_scopes))


