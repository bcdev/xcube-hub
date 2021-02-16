# Format error response and append status code.
import hashlib
import os

import flask
import requests
from jose import jwt
from requests import HTTPError

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


def get_management_token():
    client_id = os.environ.get("AUTH0_USER_MANAGEMENT_CLIENT_ID", None)
    if client_id is None:
        raise api.ApiError(400, "Please configure the env variable AUTH0_USER_MANAGEMENT_CLIENT_ID")

    client_secret = os.environ.get("AUTH0_USER_MANAGEMENT_CLIENT_SECRET", None)
    if client_secret is None:
        raise api.ApiError(400, "Please configure the env variable AUTH0_USER_MANAGEMENT_CLIENT_SECRET")

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
        raise api.ApiError(400, str(e))

    try:
        return res.json()["access_token"]
    except KeyError:
        raise api.ApiError(400, "System error: Could not find key 'access_token' in auth0's response")
