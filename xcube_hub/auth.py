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
from keycloak import KeycloakOpenID, KeycloakGetError
from werkzeug.exceptions import Unauthorized, Forbidden

from xcube_hub import util
from xcube_hub.typedefs import JsonObject

_ISS_TO_PROVIDER = {
    "https://xcube-gen.brockmann-consult.de/": 'xcube',
    "https://edc.eu.auth0.com/": 'auth0',
    "https://test/": 'mocker',
    "https://192-171-139-82.sslip.io/auth/realms/cate": "jasmin"
}


class AuthProvider(ABC):
    _claims = {}

    @abstractmethod
    def verify_token(self, token):
        """
        Get a key value
        :param token:
        :return:
        """

    @abstractmethod
    def get_email(self, claims):
        """
        Get a key value
        :param claims:
        :return:
        """


class Auth(AuthProvider):
    f"""
    A key-value pair database interface connector class (e.g. to redis)
    
    Defines abstract methods fro getting, deleting and putting key value pairs
    
    """

    _instance = None

    def __init__(self, iss: Optional[str] = None, audience: Optional[str] = None, **kwargs):
        auth0_domain = util.maybe_raise_for_env("AUTH0_DOMAIN")

        iss = iss or f"https://{auth0_domain}/"

        provider = _ISS_TO_PROVIDER.get(iss)

        self._provider = self._new_auth_provider(audience=audience, provider=provider, **kwargs)
        self._claims = dict()
        self._token = ""

    def verify_token(self, token: str) -> Optional[JsonObject]:
        """
        Get a key value
        :param token:
        :return:
        """

        claims = self._provider.verify_token(token)

        if not claims:
            raise Forbidden(description="Access denied. Invalid claims.")

        self._claims = claims
        self._token = token
        return claims

    @property
    def permissions(self):
        permissions = []
        if 'permissions' in self._claims:
            permissions = self._claims.get("permissions")
        elif 'scope' in self._claims:
            permissions = self._claims.get("scope").split(' ')

        return permissions

    # noinspection InsecureHash
    @property
    def user_id(self) -> str:
        email = self.email

        res = hashlib.md5(email.encode())

        return 'a' + res.hexdigest()

    @property
    def token(self):
        return self._token

    @property
    def email(self):
        return self.get_email(self._claims)

    def get_email(self, claims: Optional[Dict]):
        claims = claims or self._claims
        return self._provider.get_email(claims)

    def _new_auth_provider(self, audience: str, provider: Optional[str] = None, **kwargs) -> "AuthProvider":
        """
        Return a new database instance.

        :param provider: Cache provider (redis, leveldb, default leveldb)
        :param kwargs: Keyword-arguments passed to ``Database`` constructor.
        """

        if provider == 'auth0':
            return _Auth0(audience=audience, **kwargs)
        elif provider == 'xcube':
            return _AuthXcube(audience=audience, **kwargs)
        elif provider == 'jasmin':
            return _Keycloak(audience='cate', **kwargs)
        elif provider == 'mocker':
            return _AuthMocker()
        else:
            raise Unauthorized(description=f"Auth provider unknown.")

    @classmethod
    def instance(cls, iss: Optional[str] = None, audience: Optional[str] = None, refresh: bool = False, **kwargs) \
            -> "Auth":
        refresh = refresh or cls._instance is None

        if refresh:
            cls._instance = Auth(iss=iss, audience=audience, **kwargs)

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
                 domain: Optional[str] = None,
                 audience: Optional[str] = None):

        super().__init__()
        self._domain = domain or os.getenv('AUTH0_DOMAIN')
        self._audience = audience or os.getenv('XCUBE_HUB_OAUTH_AUD')
        self._algorithms = ["RS256"]

        if self._domain is None:
            raise Unauthorized(description="Auth0 error: Domain not set")

        if self._audience is None:
            raise Unauthorized(description="Auth0 error: Audience not set")

    def get_email(self, claims):
        if 'https://xcube-gen.brockmann-consult.de/user_email' not in claims:
            return "no email"
        return claims['https://xcube-gen.brockmann-consult.de/user_email']

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
            self._claims = payload
            return payload

        raise Unauthorized(description="invalid_header: Unable to find appropriate key")


class _Keycloak(AuthProvider):
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
                 domain: Optional[str] = None,
                 audience: Optional[str] = None):

        super().__init__()
        self._domain = domain or os.getenv('KEYCLOAK_DOMAIN')
        self._audience = audience or os.getenv('XCUBE_HUB_OAUTH_AUD')
        self._algorithms = ["RS256"]

        if self._domain is None:
            raise Unauthorized(description="Keycloak error: Domain not set")

        if self._audience is None:
            raise Unauthorized(description="Keycloak error: Audience not set")

        self._keycloak_openid = KeycloakOpenID(server_url=f"https://{self._domain}/auth/",
                                               client_id="cate",
                                               realm_name="cate",
                                               client_secret_key="eb305b23-252d-44c6-8efb-f6d714b87166",
                                               verify=True)

    def get_email(self, claims):
        if 'email' not in claims:
            return "no email"
        return claims['email']

    def verify_token(self, token: str) -> Dict:
        """
        Get a key value
        :param token:
        :return:
        """

        try:
            self._keycloak_openid.introspect(token)
        except KeycloakGetError as e:
            raise Unauthorized(description="invalid token: " + str(e))

        certs = self._keycloak_openid.certs()
        rsa_key = {}
        for key in certs["keys"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }

        try:
            self._claims = self._keycloak_openid.decode_token(token=token, key=rsa_key)
        except Exception as e:
            raise Unauthorized(description=str(e))

        return self._claims


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

    def get_email(self, claims):
        try:
            return claims['email']
        except KeyError:
            raise Unauthorized("Access denied. Cannot get email from token.")

    def verify_token(self, token: str) -> Dict:
        """
        Get a key value
        :param token:
        :return:
        """
        try:
            return jwt.decode(token, self._secret, audience=self._audience)
        except (JWKError, JWTError, InvalidAlgorithmError, ExpiredSignatureError) as e:
            raise Unauthorized(description=str(e))


class _AuthMocker(AuthProvider):
    """
    Mocker for unittests
    """
    return_value: Optional[Any] = None

    def __init__(self):
        super().__init__()

    def verify_token(self, token: str) -> Dict:
        return self.return_value

    def get_email(self, claims):
        return "mocker@mail.nz"
