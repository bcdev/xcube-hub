import unittest

from test.controllers.utils import create_test_token
from xcube_hub.core.geoserver import register, launch_geoserver
from xcube_hub.models.subscription import Subscription


class TestGeoserver(unittest.TestCase):
    def setUp(self) -> None:
        self._claims, self._token = create_test_token(["manage:users", "manage:cubegens"])
        self._headers = {'Authorization': f'Bearer {self._token}'}
        self._domain = "edc.eu.auth0.com"

    def test_register(self):
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

        res = register(user_id="a91f5082900b0803aa28b4679b00e93fa", subscription=subscription, headers=self._headers)
        self.assertEqual(res, True)

    def test_launch_geoserver(self):
        res = launch_geoserver(user_id="a91f5082900b0803aa28b4679b00e93fa")



if __name__ == '__main__':
    unittest.main()
