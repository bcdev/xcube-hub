import os

from jose import jwt
from werkzeug.exceptions import Unauthorized

from xcube_hub.auth import Auth


"""
controller generated to handled auth operation described at:
https://connexion.readthedocs.io/en/latest/security.html
"""


def _get_claim_from_token(token: str, tgt: str):
    unverified_claims = jwt.get_unverified_claims(token)
    tgt = unverified_claims.get(tgt)

    if tgt is None:
        raise Unauthorized(description=f"Access denied: No {tgt}.")

    return tgt


def check_oauthorization(token):
    iss = _get_claim_from_token(token=token, tgt='iss')

    # Set audience to auth0 user management audience if token claims to be a user management client token.
    # Otherwise audience wil be None and defined by environment variables
    aud = _get_claim_from_token(token=token, tgt='aud')
    user_management_aud = os.getenv("XCUBE_HUB_OAUTH_USER_MANAGEMENT_AUD", None)
    audience = user_management_aud if user_management_aud == aud else None

    # The auth provider is instantiated as a singleton.
    auth = Auth.instance(iss=iss, audience=audience)

    auth.verify_token(token=token)

    return {'scopes': auth.permissions, 'user_id': auth.user_id, 'email': auth.email, 'token': token}


def validate_scope_oauthorization(required_scopes, token_scopes):
    return set(required_scopes).issubset(set(token_scopes))


