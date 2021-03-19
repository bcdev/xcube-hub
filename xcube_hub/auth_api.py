from abc import abstractmethod, ABC
from typing import Optional
from werkzeug.exceptions import Unauthorized

from xcube_hub.typedefs import JsonObject

_ISS_TO_PROVIDER = {
    "https://xcube-gen.brockmann-consult.de/": 'xcube',
    "https://edc.eu.auth0.com/": 'auth0',
    "https://test/": 'mocker',
    "https://192-171-139-82.sslip.io/auth/realms/cate": "jasmin"
}


class AuthApiProvider(ABC):
    @abstractmethod
    def add_user(self):
        pass

    @abstractmethod
    def add_client(self):
        pass


class AuthApi(ABC):
    f"""
    A key-value pair database interface connector class (e.g. to redis)
    
    Defines abstract methods fro getting, deleting and putting key value pairs
    
    """

    _instance = None
    _provider = None

    def __init__(self, iss: str, token: str):
        self._token = token
        self._headers = {'Authorization': f'Bearer {token}'}
        provider = _ISS_TO_PROVIDER.get(iss)
        if provider is None:
            raise Unauthorized(description=f"Issuer {iss} unknown.")

        self._provider = self._new_auth_api_provider(provider=provider)

    def add_user(self, payload: JsonObject):
        pass
        # r = requests.post(f"https://{self._end_point}/users", json=payload, headers=self._headers)
        # try:
        #     r.raise_for_status()
        # except HTTPError as e:
        #     raise api.ApiError(r.status_code, str(e))

    def add_client(self, payload: JsonObject):
        pass
        # r = requests.post(f"https://{self._end_point}/users", json=payload, headers=self._headers)
        # try:
        #     r.raise_for_status()
        # except HTTPError as e:
        #     raise api.ApiError(r.status_code, str(e))

    def _new_auth_api_provider(self, provider: str, **kwargs) -> "AuthApiProvider":
        """
        Return a new database instance.

        :param provider: Cache provider (redis, leveldb, default leveldb)
        :param kwargs: Keyword-arguments passed to ``Database`` constructor.
        """

        if provider == 'auth0':
            return _Auth0Api()
        # elif provider == 'jasmin':
        #     return _Keycloak(audience='cate', **kwargs)
        # elif provider == 'mocker':
        #     return _AuthMocker()
        else:
            raise Unauthorized(description=f"Provider {provider} unknown.")

    @classmethod
    def instance(cls, iss: Optional[str] = None, token: Optional[str] = None, refresh: bool = False) \
            -> "AuthApi":
        refresh = refresh or cls._instance is None
        if refresh:
            cls._instance = AuthApi(iss=iss, token=token)

        return cls._instance


class _Auth0Api(AuthApiProvider):
    def add_user(self):
        pass
