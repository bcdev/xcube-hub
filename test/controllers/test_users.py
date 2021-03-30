import secrets
import unittest
from dotenv import load_dotenv
from test import BaseTestCase


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


if __name__ == '__main__':
    unittest.main()
