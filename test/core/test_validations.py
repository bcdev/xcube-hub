import os

from dotenv import load_dotenv

from test import BaseTestCase
from xcube_hub import api
from xcube_hub.core.validations import validate_env


class TestValidations(BaseTestCase):
    def setUp(self):
        load_dotenv(dotenv_path='test/.env')

    def test_validate_env(self):
        res = validate_env()
        self.assertTrue(res)

        del os.environ['AUTH0_USER_MANAGEMENT_CLIENT_ID']
        with self.assertRaises(api.ApiError) as e:
            validate_env()

        self.assertEqual("Env var AUTH0_USER_MANAGEMENT_CLIENT_ID required.", str(e.exception))


if __name__ == '__main__':
    import unittest

    unittest.main()
