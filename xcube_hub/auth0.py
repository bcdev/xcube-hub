# Format error response and append status code.
import hashlib
import json
from functools import wraps
from typing import Sequence
from urllib.request import urlopen
import flask
import requests
from jose import jwt

from xcube_hub import api
from xcube_hub.keyvaluedatabase import KeyValueDatabase

AUTH0_DOMAIN = 'edc.eu.auth0.com'
ALGORITHMS = ["RS256"]
API_IDENTIFIER = 'https://xcube-gen.brockmann-consult.de/api/v1/'


def get_token_auth_header():
    """Obtains the access token from the Authorization Header
    """
    auth = flask.request.headers.get("Authorization", None)
    if not auth:
        raise api.ApiError(403, "Missing authorization header.")

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise api.ApiError(401, "invalid_header: Authorization header must start with Bearer")
    elif len(parts) == 1:
        raise api.ApiError(401, "invalid_header: Token not found")
    elif len(parts) > 2:
        raise api.ApiError(401, "invalid_header: Authorization header must be Bearer token")

    token = parts[1]
    return token


def requires_permissions(required_scope: Sequence):
    """Determines if the required scope is present in the access token
    Args:
        required_scope (str): The scope required to access the resource
    """
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("permissions"):
        token_scopes = unverified_claims["permissions"]
        res = set(required_scope) & set(token_scopes)
        if len(res) == 0:
            raise api.ApiError(403, "access denied: Insufficient privileges for this operation.")


def _get_user_info_from_auth0(token, user_id: str):
    kv = KeyValueDatabase.instance()
    user_info = kv.get(user_id + '_user_info')
    if user_info:
        return user_info

    endpoint = "https://edc.eu.auth0.com/userinfo"
    headers = {'Authorization': 'Bearer %s' % token}

    req = requests.get(endpoint, headers=headers)
    if req.status_code >= 400:
        raise api.ApiError(req.status_code, req.reason)

    user_info = req.json()
    if not kv.set(user_id + '_user_info', user_info):
        raise api.ApiError(401, "System Error: Could not use cache.")

    return user_info


def raise_for_invalid_user_id(user_id: str):
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    if 'gty' in unverified_claims and unverified_claims['gty'] == 'client-credentials':
        return True

    user_info = _get_user_info_from_auth0(token, user_id)

    if 'name' not in user_info:
        raise api.ApiError(403, "access denied: Could not read name from user info.")

    name = user_info['name']
    # noinspection InsecureHash
    res = hashlib.md5(name.encode())
    name = 'a' + res.hexdigest()
    if user_id != name:
        raise api.ApiError(403, "access denied: Insufficient privileges for this operation.")

    return True


def requires_auth0(f):
    """Determines if the access token is valid
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        json_url = urlopen("https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")
        jwks = json.loads(json_url.read())

        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.JWTError:
            raise api.ApiError(401, "invalid_header: Invalid header. Use an RS256 signed JWT Access Token")
        if unverified_header["alg"] == "HS256":
            raise api.ApiError(401, "invalid_header: Invalid header. Use an RS256 signed JWT Access Token")
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_IDENTIFIER,
                    issuer="https://" + AUTH0_DOMAIN + "/"
                )
            except jwt.ExpiredSignatureError:
                raise api.ApiError(403, "access denied: token is expired")
            except jwt.JWTClaimsError:
                raise api.ApiError(401, "invalid_claims: please check the audience and issuer")
            except Exception:
                raise api.ApiError(401, "invalid_header: Unable to parse authentication")

            # noinspection PyProtectedMember
            flask._request_ctx_stack.top.current_user = payload

            return f(*args, **kwargs)

        raise api.ApiError(401, "invalid_header: Unable to find appropriate key")

    return decorated
