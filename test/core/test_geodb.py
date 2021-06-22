import unittest
from unittest.mock import patch

import requests_mock
from dotenv import load_dotenv

from xcube_hub import api
from xcube_hub.core import geodb
from xcube_hub.models.subscription import Subscription


class TestGeoDB(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv(dotenv_path='test/.env')

    @requests_mock.Mocker()
    @patch('xcube_hub.core.oauth.get_token', return_value='atoken')
    def test_register(self, m, token_p):
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

        user = [{
            "user_name": f"geodb_{subscription.guid}",
            "start_date": f"{subscription.start_date}",
            "subscription": f"{subscription.plan}",
            "cells": int(subscription.units)
        }]

        m.post("https://stage.xcube-geodb.brockmann-consult.de/geodb_user_info", json=user,
               headers={'Authorization': 'Bearer atoken'})
        res = geodb.register(subscription=subscription, raise_on_exist=True)

        self.assertTrue(res)

        m.post("https://stage.xcube-geodb.brockmann-consult.de/geodb_user_info", json=user,
               headers={'Authorization': 'Bearer atoken'}, status_code=401)

        with self.assertRaises(api.ApiError) as e:
            geodb.register(subscription=subscription, raise_on_exist=True)

        self.assertEqual("401 Client Error: None for url: https://stage.xcube-geodb.brockmann-consult.de/"
                         "geodb_user_info", str(e.exception))

        m.post("https://stage.xcube-geodb.brockmann-consult.de/geodb_user_info", json=user,
               headers={'Authorization': 'Bearer atoken'}, status_code=409)

        res = geodb.register(subscription=subscription, raise_on_exist=False)

        self.assertEqual(409, res)


if __name__ == '__main__':
    unittest.main()
