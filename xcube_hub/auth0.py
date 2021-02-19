# Format error response and append status code.
import hashlib
import json
import os
from typing import Sequence, Union
from urllib.request import urlopen

import flask
import requests
from jose import jwt
from requests import HTTPError
from werkzeug.exceptions import Forbidden, Unauthorized

from xcube_hub import api
from xcube_hub.keyvaluedatabase import KeyValueDatabase

AUTH0_DOMAIN = 'edc.eu.auth0.com'
ALGORITHMS = ["RS256"]
DEFAULT_API_IDENTIFIER = 'https://xcube-gen.brockmann-consult.de/api/v2/'
API_AUTH_IDENTIFIER = 'https://edc.eu.auth0.com/api/v2/'


def get_user_info_from_auth0(token, user_id: str):
    kv = KeyValueDatabase.instance()
    user_info = kv.get(user_id + '_user_info')
    if user_info and isinstance(user_info, dict):
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


def raise_for_invalid_user_id(token: str, user_id: str):
    unverified_claims = jwt.get_unverified_claims(token)
    if 'gty' in unverified_claims and unverified_claims['gty'] == 'client-credentials':
        return True

    user_info = get_user_info_from_auth0(token, user_id)

    if 'name' not in user_info:
        raise api.ApiError(403, "access denied: Could not read name from user info.")

    name = user_info['name']
    # noinspection InsecureHash
    res = hashlib.md5(name.encode())
    name = 'a' + res.hexdigest()
    if user_id != name:
        raise api.ApiError(403, "access denied: Insufficient privileges for this operation.")

    return True


def get_token_auth_header():
    """Obtains the access token from the Authorization Header
    """
    auth = flask.request.headers.get("Authorization", None)
    if not auth:
        raise Forbidden(description="Missing authorization header.")

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise Unauthorized(description="invalid_header: Authorization header must start with Bearer")
    elif len(parts) == 1:
        raise Unauthorized(description="invalid_header: Token not found")
    elif len(parts) > 2:
        raise Unauthorized(description="invalid_header: Authorization header must be Bearer token")

    token = parts[1]
    return token


def get_management_token():
    client_id = os.environ.get("AUTH0_USER_MANAGEMENT_CLIENT_ID", None)
    if client_id is None:
        raise Unauthorized(description="Please configure the env variable AUTH0_USER_MANAGEMENT_CLIENT_ID")

    client_secret = os.environ.get("AUTH0_USER_MANAGEMENT_CLIENT_SECRET", None)
    if client_secret is None:
        raise Unauthorized(description="Please configure the env variable AUTH0_USER_MANAGEMENT_CLIENT_SECRET")

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": "https://edc.eu.auth0.com/api/v2/",
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


def verify_token(token: str, audience: Union[str, Sequence]):
    json_url = urlopen("https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")
    jwks = json.loads(json_url.read())

    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        raise Unauthorized(description="invalid_header: Invalid header. Use an RS256 signed JWT Access Token")
    if unverified_header["alg"] == "HS256":
        raise Unauthorized(description="invalid_header: Invalid header. Use an RS256 signed JWT Access Token")
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
                audience=audience,
                issuer="https://" + AUTH0_DOMAIN + "/"
            )
        except jwt.ExpiredSignatureError:
            raise Forbidden(description="access denied: token is expired")
        except jwt.JWTClaimsError:
            raise Unauthorized(description="invalid_claims: please check the audience and issuer")
        except Exception:
            raise Unauthorized(description="invalid_header: Unable to parse authentication")

        # noinspection PyProtectedMember
        flask._request_ctx_stack.top.current_user = payload

        return payload

    raise Unauthorized(description="invalid_header: Unable to find appropriate key")
