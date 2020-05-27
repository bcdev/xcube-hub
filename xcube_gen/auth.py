# Format error response and append status code.
import hashlib
import json
from functools import wraps
from typing import Sequence
from urllib.request import urlopen
import flask
import requests
from jose import jwt

AUTH0_DOMAIN = 'edc.eu.auth0.com'
ALGORITHMS = ["RS256"]
API_IDENTIFIER = 'https://xcube-gen.brockmann-consult.de/api/v1/'


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """Obtains the access token from the Authorization Header
    """
    auth = flask.request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                             "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must start with"
                             " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must be"
                             " Bearer token"}, 401)

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
            raise AuthError({"code": "access denied", "description": "Insufficient privileges for this operation."},
                            403)


def _get_userinfo_from_auth0(token):

    endpoint = "https://edc.eu.auth0.com/userinfo"
    headers = {'Authorization': 'Bearer %s' % token}

    req = requests.get(endpoint, headers=headers)
    if req.status_code >= 400:
        raise AuthError({"code": "access denied",
                         "description": req.reason},
                        req.status_code)

    return req.json()


def raise_for_invalid_user(user_id: str):
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    if 'qty' in unverified_claims and unverified_claims['qty'] == 'client-credentials':
        return True
    user_info = _get_userinfo_from_auth0(token)
    name = user_info['name']
    # noinspection InsecureHash
    res = hashlib.md5(name.encode())
    name = 'a' + res.hexdigest()
    if user_id != name:
        raise AuthError({"code": "access denied", "description": "Insufficient privileges for this operation."}, 403)

    return True


def requires_auth(f):
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
            raise AuthError({"code": "invalid_header",
                             "description":
                                 "Invalid header. "
                                 "Use an RS256 signed JWT Access Token"}, 401)
        if unverified_header["alg"] == "HS256":
            raise AuthError({"code": "invalid_header",
                             "description":
                                 "Invalid header. "
                                 "Use an RS256 signed JWT Access Token"}, 401)
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
                raise AuthError({"code": "token_expired",
                                 "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                 "description":
                                     "incorrect claims,"
                                     " please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                 "description":
                                     "Unable to parse authentication"
                                     " token."}, 401)

            # noinspection PyProtectedMember
            flask._request_ctx_stack.top.current_user = payload

            return f(*args, **kwargs)

        raise AuthError({"code": "invalid_header",
                         "description": "Unable to find appropriate key"}, 401)

    return decorated
