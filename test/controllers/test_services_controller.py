import unittest
from unittest.mock import patch, MagicMock

from test import BaseTestCase
from xcube_hub import api
from xcube_hub.controllers import services
from xcube_hub.models.subscription import Subscription
from xcube_hub.subscription_api import SubscriptionApi

_SERVICES = ['xcube_gen', 'xcube_serve', 'xcube_geodb']

_SUB = Subscription(
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


class TestServices(BaseTestCase):
    def setUp(self) -> None:
        self._sub_api = SubscriptionApi.instance(iss="https://test/", refresh=True)

    def test_get_services(self):
        res = services.get_services()

        self.assertEqual((['xcube_gen', 'xcube_serve', 'xcube_geodb'], 200), res)

        with patch('xcube_hub.core.services.get_services', side_effect=api.ApiError(400, 'Error')) as p:
            res = services.get_services()

            self.assertEqual(400, res[1])
            self.assertEqual('Error', res[0]['message'])

    def test_put_subscription_to_service(self):
        res = services.put_subscription_to_service('xcube_gen', {}, dict(iss="https://test/", token='sdfsdaf'))

        self.assertEqual(200, res[1])
        self.assertDictEqual(_SUB.to_dict(), res[0])

        error = api.ApiError(400, 'Error')

        self._sub_api._provider.add_subscription = MagicMock(name='add_subscription',
                                                             side_effect=error,
                                                             return_value=error.response)

        res = services.put_subscription_to_service('xcube_gen', {}, dict(iss="https://test/", token='sdfsdaf'))

        self.assertEqual(400, res[1])
        self.assertEqual('Error', res[0]['message'])

    def test_get_subscription_from_service(self):
        res = services.get_subscription_from_service('xcube_gen', 'sub_id', dict(iss="https://test/", token='sdfsdaf'))

        self.assertEqual(200, res[1])
        self.assertDictEqual(_SUB.to_dict(), res[0])

        error = api.ApiError(400, 'Error')

        self._sub_api._provider.get_subscription = MagicMock(name='get_subscription',
                                                             side_effect=error,
                                                             return_value=error.response)

        res = services.get_subscription_from_service('xcube_gen', 'sub_id', dict(iss="https://test/", token='sdfsdaf'))

        self.assertEqual(400, res[1])
        self.assertEqual('Error', res[0]['message'])

    def test_delete_subscription_from_service(self):
        res = services.delete_subscription_from_service('xcube_gen', 'sub_id',
                                                        dict(iss="https://test/", token='sdfsdaf'))

        self.assertEqual(200, res[1])
        self.assertEqual('ab123', res[0])

        error = api.ApiError(400, 'Error')

        self._sub_api._provider.delete_subscription = MagicMock(name='delete_subscription',
                                                                side_effect=error,
                                                                return_value=error.response)

        res = services.delete_subscription_from_service('xcube_gen', 'sub_id',
                                                        dict(iss="https://test/", token='sdfsdaf'))

        self.assertEqual(400, res[1])
        self.assertEqual('Error', res[0]['message'])


if __name__ == '__main__':
    unittest.main()
