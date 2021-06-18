import unittest
from unittest.mock import patch, MagicMock

import boto3
import requests_mock
from dotenv import load_dotenv
from moto import mock_s3
from werkzeug.exceptions import Unauthorized

from test.controllers.utils import create_test_token

# noinspection PyProtectedMember
from xcube_hub.subscription_api import SubscriptionApi, _SubscriptionMockApi, _ISS_TO_PROVIDER, _SubscriptionKeycloakApi, \
    _SubscriptionAuth0Api
from xcube_hub.database import DEFAULT_DB_BUCKET_NAME
from xcube_hub.models.subscription import Subscription
from xcube_hub.models.user import User
from xcube_hub.models.user_app_metadata import UserAppMetadata
from xcube_hub.models.user_user_metadata import UserUserMetadata


class TestAuthApi(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv(dotenv_path='test/.env')
        self._claims, self._token = create_test_token(["manage:users", "manage:cubegens"])

    def test_auth_api(self):
        for k, v in _ISS_TO_PROVIDER.items():
            api = SubscriptionApi(iss=k, token=self._token)
            if v == 'mocker':
                self.assertIsInstance(api._provider, _SubscriptionMockApi)
            elif v == 'keycloak':
                self.assertIsInstance(api._provider, _SubscriptionKeycloakApi)
            elif v == 'auth0':
                self.assertIsInstance(api._provider, _SubscriptionAuth0Api)

        with self.assertRaises(Unauthorized) as e:
            api = SubscriptionApi(iss='ff', token=self._token)

        self.assertEqual('401 Unauthorized: Issuer ff unknown.', str(e.exception))


@unittest.skip
@requests_mock.Mocker()
class TestAuth0Api(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv(dotenv_path='test/.env')
        self._claims, self._token = create_test_token(["manage:users", "manage:cubegens"])
        self._headers = {'Authorization': f'Bearer {self._token}'}
        self._domain = "edc.eu.auth0.com/api/v2"

    def test_get_subscription(self, m):
        subscription = Subscription(
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

        user = User(
            user_id='ab123',
            email="peter.pettigrew@mail.com",
            username="peter.pettigrew@mail.com",
            password="fv",
            given_name='Peter',
            family_name='Pettigrew',
            connection="",
            user_metadata=UserUserMetadata(subscriptions=dict(xcube_gen=subscription))
        )

        m.get("https://edc.eu.auth0.com/api/v2/users/auth0%7Ca91f5082900b0803aa28b4679b00e93fa", json=user.to_dict(),
              headers=self._headers)
        m.post(f"https://edc.eu.auth0.com/api/v2/users", json=user.to_dict(), headers=self._headers)

        m.get("https://edc.eu.auth0.com/api/v2/users/auth0%7Cab123", json=user.to_dict(), headers=self._headers)

        service_id = "xcube_gen"
        subscription_id = "ab123"
        auth_api = SubscriptionApi.instance(iss="https://edc.eu.auth0.com/", token=self._token)
        res = auth_api.get_subscription(service_id=service_id, subscription_id=subscription_id)
        self.assertDictEqual(subscription.to_dict(), res.to_dict())

    @mock_s3
    def test_add_subscription(self, m):
        service_id = "xcube_gen"

        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=DEFAULT_DB_BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
        punits_request_1 = dict(punits=dict(total_count=50000,
                                            user_name='heinrich@gmail.com',
                                            price_amount=200,
                                            price_currency='€'))

        user = User(
            user_id='a91f5082900b0803aa28b4679b00e93fa',
            email="peter.pettigrew@mail.com",
            given_name="Peter",
            family_name="Pettigrew",
            username="peter.pettigrew@mail.com",
            password="fbsdb",
            user_metadata=UserUserMetadata(subscriptions={}),
            app_metadata=UserAppMetadata(),
            connection=""
        )

        m.get("https://edc.eu.auth0.com/api/v2/users/auth0%7Ca91f5082900b0803aa28b4679b00e93fa", headers=self._headers,
              json=user.to_dict())

        m.patch("https://edc.eu.auth0.com/api/v2/users/a91f5082900b0803aa28b4679b00e93fa", json=user.to_dict(),
                headers=self._headers)

        subscription = Subscription(
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

        # test user is created
        m.get(f"https://{self._domain}/services/{service_id}/subscriptions/a91f5082900b0803aa28b4679b00e93fa",
              json=user.to_dict(),
              headers=self._headers)

        m.get(f"https://{self._domain}/services/{service_id}/subscriptions/abs123",
              headers=self._headers, status_code=404)
        m.post(f"https://{self._domain}/services/{service_id}/subscriptions", json={}, headers=self._headers)
        m.patch('https://edc.eu.auth0.com/api/v2/users/auth0%7Ca91f5082900b0803aa28b4679b00e93fa', json={})
        m.post('https://edc.eu.auth0.com/api/v2/users/auth0%7Ca91f5082900b0803aa28b4679b00e93fa/roles', json={})
        m.post("https://edc.eu.auth0.com/oauth/token", json={})
        service_id = "xcube_gen"

        auth_api = SubscriptionApi.instance(iss="https://edc.eu.auth0.com/", token=self._token)
        res = auth_api.add_subscription(service_id=service_id, subscription=subscription)
        self.assertDictEqual(subscription.to_dict(), res)

        # test user exists

        m.get(f"https://{self._domain}/services/{service_id}/subscriptions/a91f5082900b0803aa28b4679b00e93fa",
              json=user.to_dict(),
              headers=self._headers)
        m.post(f"https://{self._domain}/services/{service_id}/subscriptions", json=subscription.to_dict(),
               headers=self._headers)

        service_id = "xcube_gen"

        res = auth_api.add_subscription(service_id=service_id, subscription=subscription)
        self.assertDictEqual(subscription.to_dict(), res)
        # Testing error 409 when a subscription exist already. Removed on request should be reintroduced header
        # controlled
        # user.user_metadata.subscriptions['xcube_gen'] = {}
        # m.get(f"https://{self._domain}/services/{service_id}/subscriptions/a91f5082900b0803aa28b4679b00e93fa",
        #       json=user.to_dict(), headers=self._headers)
        # with self.assertRaises(api.ApiError) as e:
        #     res = auth_api.add_subscription(service_id=service_id, subscription=subscription)
        #
        # self.assertEqual("The subscription a91f5082900b0803aa28b4679b00e93fa exists for service xcube_gen.",
        #                  str(e.exception))
        # self.assertEqual(409, e.exception.status_code)

        # m.post(f"https://{self._domain}//services/{service_id}/subscriptions", json=user.to_dict(),
        #        headers=self._headers, reason="ERROR", status_code=409)
        # del user.user_metadata.subscriptions['xcube_gen']
        #
        # m.get(f"https://{self._domain}/users/a91f5082900b0803aa28b4679b00e93fa", json=user.to_dict(),
        #       headers=self._headers)
        #
        # with self.assertRaises(api.ApiError) as e:
        #     res = auth_api.add_subscription(service_id=service_id, subscription=subscription)
        #
        # self.assertEqual("409 Client Error: ERROR for url: https://edc.eu.auth0.com/users",
        #                  str(e.exception))
        # self.assertEqual(409, e.exception.status_code)

    @unittest.skip
    def test_add_subscription_geodb(self, m):
        subscription = Subscription(
            subscription_id='a91f5082900b0803aa28b4679b00e93fa',
            email="peter.pettigrew@mail.com",
            plan='manage',
            guid='dfvdsv',
            client_id='fdvdv',
            client_secret='sdfvsdvdf',
            units=1000.0,
            unit='cells',
            first_name='Peter',
            last_name='Pettigrew',
            start_date="2000-01-01",
        )

        user = User(
            user_id='a91f508290 0b0803aa28b4679b00e93fa',
            email="peter.pettigrew@mail.com",
            given_name="Peter",
            family_name="Pettigrew",
            username="peter.pettigrew@mail.com",
            password="fbsdb",
            user_metadata=UserUserMetadata(subscriptions={}),
            app_metadata=UserAppMetadata(),
            connection=""
        )

        with patch('xcube_hub.core.geodb.register', return_value=True) as p:
            m.delete(f"https://edc.eu.auth0.com/api/v2/users/auth0%7Ca91f5082900b0803aa28b4679b00e93fa/roles",
                     headers=self._headers)
            m.post(f"https://edc.eu.auth0.com/api/v2/users/auth0%7Ca91f5082900b0803aa28b4679b00e93fa/roles", json={},
                   headers=self._headers)
            m.post("https://edc.eu.auth0.com/api/v2/users", json=user.to_dict(), headers=self._headers)
            service_id = "xcube_geodb"
            auth_api = SubscriptionApi.instance(iss="https://edc.eu.auth0.com/", token=self._token)
            auth_api._provider._get_user = MagicMock(name='_get_user', return_value=None)

            sub = Subscription.from_dict(subscription.to_dict())
            res = auth_api.add_subscription(service_id=service_id, subscription=sub)

            self.assertEqual('rol_IraXoXpSlA408Hqq', res.role)
            res = res.to_dict()
            res['role'] = None
            self.assertDictEqual(subscription.to_dict(), res)

            subscription.plan = 'freetrial'
            sub = Subscription.from_dict(subscription.to_dict())
            res = auth_api.add_subscription(service_id=service_id, subscription=sub)

            self.assertEqual('rol_nF3PSuWkOJLk1mkm', res.role)
            res = res.to_dict()
            res['role'] = None
            self.assertDictEqual(subscription.to_dict(), res)

            subscription.plan = 'user'
            sub = Subscription.from_dict(subscription.to_dict())
            res = auth_api.add_subscription(service_id=service_id, subscription=sub)

            self.assertEqual('rol_7p5tk27ORUhYETFI', res.role)
            res = res.to_dict()
            res['role'] = None
            self.assertDictEqual(subscription.to_dict(), res)


    def test_delete_subscription(self, m):
        user = User(
            user_id='a91f5082900b0803aa28b4679b00e93fa',
            email="peter.pettigrew@mail.com",
            given_name="Peter",
            family_name="Pettigrew",
            username="peter.pettigrew@mail.com",
            password="fbsdb",
            user_metadata=UserUserMetadata(subscriptions={"xcube_gen": {}}),
            app_metadata=UserAppMetadata(),
            connection=""
        )

        m.patch(f"https://{self._domain}/users/auth0%7Ca91f5082900b0803aa28b4679b00e93fa", json={}, headers=self._headers)
        m.get(f"https://{self._domain}/users/auth0%7Ca91f5082900b0803aa28b4679b00e93fa", json=user.to_dict(),
              headers=self._headers)

        service_id = "xcube_gen"
        auth_api = SubscriptionApi.instance(iss="https://edc.eu.auth0.com/", token=self._token)
        res = auth_api.delete_subscription(service_id=service_id, subscription_id="ab123")
        self.assertEqual("ab123", res)


class TestMockApi(unittest.TestCase):
    def test_methods(self):
        subscription = Subscription(
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

        auth_api = _SubscriptionMockApi()
        res = auth_api.get_subscription(service_id='', subscription_id='')
        self.assertDictEqual(subscription.to_dict(), res.to_dict())

        res = auth_api.add_subscription(service_id='', subscription=subscription)
        self.assertDictEqual(subscription.to_dict(), res)

        res = auth_api.delete_subscription(service_id='', subscription_id='')
        self.assertEqual('ab123', res)


if __name__ == '__main__':
    unittest.main()
