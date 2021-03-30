import os
from abc import abstractmethod, ABC
from typing import Optional

import requests
from keycloak import KeycloakGetError
from keycloak.exceptions import KeycloakError
from keycloak.keycloak_admin import KeycloakAdmin
from requests import HTTPError
from werkzeug.exceptions import Unauthorized
from urllib.parse import urlparse

from xcube_hub import api, util
from xcube_hub.core import users, punits
from xcube_hub.core.geodb import register_user
from xcube_hub.models.subscription import Subscription
from xcube_hub.models.user import User
from xcube_hub.models.user_user_metadata import UserUserMetadata

_ISS_TO_PROVIDER = {
    "https://edc.eu.auth0.com/": 'auth0',
    "https://test/": 'mocker',
    "https://192-171-139-82.sslip.io/auth/realms/cate": "keycloak",
    "https://xcube-users.brockmann-consult.de/auth/realms/xcube": "keycloak",
    "https://cateusers.climate.esa.int/auth/realms/cate": "keycloak",
}


class AuthApiProvider(ABC):
    @abstractmethod
    def add_subscription(self, service_id: str, subscription: Subscription):
        """
        Get a key value
        :param service_id:
        :param subscription:
        :return:
        """

    @abstractmethod
    def get_subscription(self, service_id: str, subscription_id: str):
        """
        Get a key value
        :param service_id:
        :param subscription_id:
        :return:
        """

    @abstractmethod
    def delete_subscription(self, service_id: str, subscription_id: str):
        """
        Get a key value
        :param service_id:
        :param subscription_id:
        :return:
        """


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

        self._provider = AuthApi._new_auth_api_provider(iss=iss, token=token)

    def add_subscription(self, service_id: str, subscription: Subscription):
        return self._provider.add_subscription(service_id=service_id, subscription=subscription)

    def get_subscription(self, service_id: str, subscription_id: str):
        return self._provider.get_subscription(service_id=service_id, subscription_id=subscription_id)

    def delete_subscription(self, service_id: str, subscription_id: str):
        return self._provider.delete_subscription(service_id=service_id, subscription_id=subscription_id)

    @classmethod
    def _new_auth_api_provider(cls, iss: str, token: str, **kwargs) -> "AuthApiProvider":
        """
        Return a new database instance.

        :param provider: Cache provider (redis, leveldb, default leveldb)
        :param kwargs: Keyword-arguments passed to ``Database`` constructor.
        """
        provider = _ISS_TO_PROVIDER.get(iss)
        if provider is None:
            raise Unauthorized(description=f"Issuer {iss} unknown.")

        domain = urlparse(iss).netloc

        if provider == 'auth0':
            return _Auth0Api(token=token, domain=domain)
        elif provider == 'keycloak':
            return _KeycloakApi(token=token, **kwargs)
        else: # provider == 'mocker'
            return _MockerApi()

    @classmethod
    def instance(cls, iss: Optional[str] = None, token: Optional[str] = None, refresh: bool = False) \
            -> "AuthApi":
        refresh = refresh or cls._instance is None
        if refresh:
            cls._instance = AuthApi(iss=iss, token=token)

        return cls._instance


class _Auth0Api(AuthApiProvider):
    def __init__(self, token: str, domain: Optional[str] = None):
        self._domain = domain
        self._headers = {'Authorization': f'Bearer {token}'}

    def add_subscription(self, service_id: str, subscription: Subscription):
        user = self._get_user(user_id=subscription.subscription_id, raising=False)

        if user is None:
            user = User()
            user.user_id = util.create_user_id_from_email(subscription.email)
            user.email = subscription.email
            user.first_name = subscription.first_name
            user.last_name = subscription.last_name
            user.user_metadata = UserUserMetadata(subscriptions={})
            user = users.supplement_user(user=user)

        subscription.subscription_id = user.user_id
        subscription.client_id = user.user_metadata.client_id
        subscription.client_secret = user.user_metadata.client_secret

        if service_id in user.user_metadata.subscriptions:
            raise api.ApiError(409, f"The subscription {subscription.subscription_id} exists for service {service_id}.")

        user.user_metadata.subscriptions[service_id] = subscription

        if service_id == "xcube_geodb":
            user.app_metadata.geodb_role = "geodb_" + subscription.guid
            register_user(user_id=user.user_id, subscription=subscription, headers=self._headers)

        if service_id == "xcube_gen":
            punits.add_punits(user_id=user.email,
                              punits_request=dict(punits=dict(total_count=int(subscription.units))))

        r = requests.post(f"https://{self._domain}/users", json=user.to_dict(), headers=self._headers)

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise api.ApiError(r.status_code, str(e))

        return subscription

    def get_subscription(self, service_id: str, subscription_id: str):
        r = requests.get(f"https://{self._domain}/users/{subscription_id}", headers=self._headers)

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise api.ApiError(r.status_code, str(e))

        user = User.from_dict(r.json())

        return user.user_metadata.subscriptions[service_id]

    def delete_subscription(self, service_id: str, subscription_id: str):
        user = self._get_user(user_id=subscription_id)

        user_metadata = user.user_metadata
        del user_metadata.subscriptions[service_id]

        payload = dict(user_metadata=user_metadata.to_dict())

        r = requests.patch(f"https://{self._domain}/users/{subscription_id}", json=payload, headers=self._headers)

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise api.ApiError(r.status_code, str(e))

        return subscription_id

    def _get_user(self, user_id, raising=True) -> Optional[User]:
        r = requests.get(f"https://{self._domain}/users/{user_id}", headers=self._headers)

        try:
            r.raise_for_status()
        except HTTPError as e:
            if raising:
                raise api.ApiError(r.status_code, str(e))
            else:
                return None

        return User.from_dict(r.json())


class _KeycloakApi(AuthApiProvider):
    _payload_client = {
        "clientId": "helge2",
        "enabled": True,
        "name": "helge2",
        "protocol": "openid-connect",
        "standardFlowEnabled": True,
        "publicClient": False,
        "directAccessGrantsEnabled": True,
        "redirectUris": ["http://localhost:3000"],
        "serviceAccountsEnabled": True,
        "protocolMappers": [
            {
                "name": "geodb_role16",
                "protocol": "openid-connect",
                "protocolMapper": "oidc-hardcoded-claim-mapper",
                "config": {
                    "tokenClaimName": "geodb_role16",
                    "claimValue": "test",
                    "claimJsonType": "string",
                    "id.token.claim": "true",
                    "access.token.claim": "true",
                    "userinfo.token.claim": "",
                    "access.tokenResponse.claim": "",
                    "claim.name": "geodb_role16",
                    "claim.value": "geodb_role6TEST",
                    "jsonType.label": "String"
                }
            }
        ]
    }

    def __init__(self,
                 token: str,
                 server_url: Optional[str] = None,
                 realm: Optional[str] = None,
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None):
        super().__init__()

        self._headers = {'Authorization': f'Bearer {token}'}
        self._server_url = server_url or os.getenv("KEYCLOAK_DOMAIN")
        self._realm = realm or os.getenv("KEYCLOAK_REALM")
        self._client_id = client_id or os.getenv("XCUBE_GEN_CLIENT_ID")
        self._client_secret = client_secret or os.getenv("XCUBE_GEN_CLIENT_SECRET")

    @property
    def admin_client(self):
        try:
            return KeycloakAdmin(server_url=self._server_url,
                                 username='example-admin',
                                 password='secret',
                                 realm_name=self._realm,
                                 client_id=self._client_id,
                                 client_secret_key=self._client_secret,
                                 verify=True)
        except KeycloakError as e:
            raise api.ApiError(e.response_code, str(e))

    def add_subscription(self, service_id: str, subscription: Subscription):
        try:
            geodb_role = f"geodb_{subscription.guid}"

            self.admin_client.create_user({
                "subscription_id": subscription.guid,
                "email": subscription.email,
                "username": subscription.email,
                "enabled": True,
                "firstName": subscription.first_name,
                "lastName": subscription.last_name,
                "attributes": {
                    "geodb_role": geodb_role
                }
            })

        except KeycloakGetError as e:
            raise api.ApiError(e.response_code, str(e))

    def get_subscription(self, service_id: str, subscription_id: str):
        raise NotImplemented("Error: The method _KeycloakApi.get_subscription has not been implemented")

    def delete_subscription(self, service_id: str, subscription_id: str):
        raise NotImplemented("Error: The method _KeycloakApi.delete_subscription has not been implemented")

    def get_user(self, user_id: str):
        try:
            return self.admin_client.get_user(user_id=user_id)
        except KeycloakGetError as e:
            raise api.ApiError(e.response_code, str(e))

    # def add_client_from_subscription(self, service_id: str, subscription: Subscription):
    #     try:
    #         redirect_uris = []
    #         geodb_role = f"geodb_{subscription.guid}"
    #         self.admin_client.create_client({
    #             "name": subscription.client_id,
    #             "clientId": subscription.client_id,
    #             "secret": subscription.client_secret,
    #             "publicClient": False,
    #             "standardFlowEnabled": True,
    #             "directAccessGrantsEnabled": True,
    #             "serviceAccountsEnabled": True,
    #             "enabled": True,
    #             "redirectUris": redirect_uris,
    #             "protocol": "openid-connect",
    #             "protocolMappers": [
    #                 {
    #                     "name": geodb_role,
    #                     "protocol": "openid-connect",
    #                     "protocolMapper": "oidc-hardcoded-claim-mapper",
    #                     "config": {
    #                         "tokenClaimName": "geodb_role",
    #                         "claimValue": geodb_role,
    #                         "claimJsonType": "string",
    #                         "id.token.claim": "true",
    #                         "access.token.claim": "true",
    #                         "userinfo.token.claim": "",
    #                         "access.tokenResponse.claim": "",
    #                         "claim.name": "geodb_role",
    #                         "claim.value": geodb_role,
    #                         "jsonType.label": "String"
    #                     }
    #                 }
    #             ]
    #         })
    #     except KeycloakGetError as e:
    #         raise api.ApiError(400, str(e))
    #


class _MockerApi(AuthApiProvider):
    def add_subscription(self, service_id: str, subscription: Subscription):
        return Subscription(
            subscription_id='ab123',
            email="peter.pettigrew@mail.com",
            plan='free',
            guid='dfvdsv',
            client_id='fdvdv',
            client_secret='sdfvsdvdf',
            units=1000,
            unit='punits',
            first_name='Peter',
            last_name='Pettigrew',
            start_date="2000-01-01",
        )

    def get_subscription(self, service_id: str, subscription_id: str):
        return Subscription(
            subscription_id='ab123',
            email="peter.pettigrew@mail.com",
            plan='free',
            guid='dfvdsv',
            client_id='fdvdv',
            client_secret='sdfvsdvdf',
            units=1000,
            unit='punits',
            first_name='Peter',
            last_name='Pettigrew',
            start_date="2000-01-01",
        )

    def delete_subscription(self, service_id: str, subscription_id: str):
        return 'ab123'
