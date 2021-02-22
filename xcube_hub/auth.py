import hashlib
import json
import os
from abc import abstractmethod, ABC
from typing import Optional, Any, Dict
from urllib.request import urlopen

import flask
from jose import jwt
from jose.exceptions import JWKError, JWTError, ExpiredSignatureError
from jwt import InvalidAlgorithmError
from werkzeug.exceptions import Unauthorized, Forbidden

from xcube_hub import api
from xcube_hub.typedefs import JsonObject


_ISS_TO_PROVIDER = {
    "https://xcube-gen.brockmann-consult.de/": 'xcube',
    "https://edc.eu.auth0.com/": 'auth0',
}


class AuthProvider(ABC):
    @abstractmethod
    def verify_token(self, key):
        """
        Get a key value
        :param key:
        :return:
        """


class Auth(AuthProvider):
    f"""
    A key-value pair database interface connector class (e.g. to redis)
    
    Defines abstract methods fro getting, deleting and putting key value pairs
    
    """

    _instance = None

    def __init__(self, provider: str, audience: str, **kwargs):
        self._provider = self._new_auth_provider(audience=audience, provider=provider, **kwargs)
        self._claims = dict()

    def verify_token(self, token: str) -> Optional[JsonObject]:
        """
        Get a key value
        :param token:
        :return:
        """

        claims = self._provider.verify_token(token)

        if not claims:
            raise Forbidden()

        self._claims = claims
        return claims

    @property
    def permissions(self):
        permissions = []
        if 'permissions' in self._claims:
            permissions = self._claims.get("permissions")
        elif 'scope' in self._claims:
            permissions = self._claims.get("scope").split(' ')

        if permissions is None:
            raise api.ApiError(403, "access denied: Insufficient permissions.")

        return permissions

    # noinspection InsecureHash
    @property
    def user_id(self) -> str:
        try:
            email = self._claims['email']
        except KeyError:
            raise Unauthorized(description="This claim does not contain an email address.")

        res = hashlib.md5(email.encode())

        return 'a' + res.hexdigest()

    def _new_auth_provider(self, audience: str, provider: Optional[str] = None, **kwargs) -> "AuthProvider":
        """
        Return a new database instance.

        :param provider: Cache provider (redis, leveldb, default leveldb)
        :param kwargs: Keyword-arguments passed to ``Database`` constructor.
        """

        if provider == 'auth0':
            return _Auth0(audience, **kwargs)
        elif provider == 'xcube':
            return _AuthXcube(audience, **kwargs)
        else:
            raise Unauthorized(description=f"Provider {provider} unknown.")

    @classmethod
    def instance(cls, iss: Optional[str] = None, refresh: bool = False, use_mocker: bool = False, **kwargs) \
            -> "Auth":
        refresh = refresh or cls._instance is None
        if refresh:
            if use_mocker:
                cls._instance = _AuthMocker
            else:
                provider = None
                try:
                    provider = _ISS_TO_PROVIDER.get(iss)
                except KeyError as e:
                    Unauthorized(description=f"Issuer {iss} unknown.")

                cls._instance = Auth(provider=provider, **kwargs)

        return cls._instance


class _Auth0(AuthProvider):
    f"""
    Redis key-value pair database implementation of KeyValueStore
    
    Defines methods for getting, deleting and putting key value pairs
    
    :param host, port, db (see also `https://github.com/andymccurdy/redis-py)`
    Example:
    ```
        db = KeyValueDatabase.instance(provider='redis', host='localhost', port=6379, db=0)
    ```
    """

    def __init__(self,
                 domain: str,
                 audience: str,
                 user_management_client_id: Optional[str] = None,
                 user_management_client_secret: Optional[str] = None):

        super().__init__()
        self._domain = os.getenv('AUTH0_DOMAIN') or domain
        self._audience = os.getenv('XCUBE_HUB_OAUTH_AUD') or audience
        self._user_management_client_id = os.getenv('AUTH0_USER_MANAGEMENT_CLIENT_ID') or user_management_client_id
        self._user_management_client_secret = os.getenv(
            'AUTH0_USER_MANAGEMENT_CLIENT_SECRET') or user_management_client_secret
        self._algorithms = ["RS256"]

    def verify_token(self, token: str) -> Dict:
        """
        Get a key value
        :param token:
        :return:
        """

        json_url = urlopen("https://" + self._domain + "/.well-known/jwks.json")
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
                    algorithms=self._algorithms,
                    audience=self._audience,
                    issuer="https://" + self._domain + "/"
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


class _AuthXcube(AuthProvider):
    f"""
    Redis key-value pair database implementation of KeyValueStore
    
    Defines methods for getting, deleting and putting key value pairs
    
    :param host, port, db (see also `https://github.com/andymccurdy/redis-py`)
    Example:
    ```
        db = KeyValueDatabase.instance(provider='leveldb', name='/tmp/testdb/', create_if_missing=True)
    ```
    """

    def __init__(self,
                 audience: Optional[str] = None,
                 secret: Optional[str] = None):

        super().__init__()
        self._audience = os.getenv('XCUBE_HUB_OAUTH_AUD') or audience
        self._secret = os.getenv('XCUBE_HUB_TOKEN_SECRET') or secret
        self._algorithms = ["HS256"]

    def verify_token(self, token: str) -> Dict:
        """
        Get a key value
        :param token:
        :return:
        """
        try:
            return jwt.decode(token, self._secret, audience=self._audience)
        except (JWKError, JWTError, InvalidAlgorithmError, ExpiredSignatureError) as e:
            raise Forbidden(description=str(e))


class _AuthMocker:
    """
    Mocker for unittests
    """
    return_value: Optional[Any] = None

    def verify_token(self, token: str) -> Dict:
        return self.return_value
