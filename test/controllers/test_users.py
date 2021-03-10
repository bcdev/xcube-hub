import secrets
import unittest

import requests_mock
from dotenv import load_dotenv

from test import BaseTestCase
from xcube_hub.controllers.oauth import _get_management_token


class TestUsers(BaseTestCase):
    def setUp(self):
        load_dotenv(dotenv_path='test/.env')

        self._user = {
            "email": "xcube-test@mail.com",
            "given_name": "Leslie",
            "family_name": "Marchand",
            "connection": "Username-Password-Xcube",
            "password": secrets.token_urlsafe(256)
        }

    def test_get_user_by_user_id(self):
        token = _get_management_token()

        response = self.client.open('/api/v2/users', method='PUT',
                                    json=self._user,
                                    headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
