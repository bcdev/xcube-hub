import os

from test import BaseTestCase
from xcube_hub import api
from xcube_hub.core.validations import validate_env, REQUIRED_ENV_VARS


class TestOauthController(BaseTestCase):
    def setUp(self):
        for env in REQUIRED_ENV_VARS:
            os.environ[env] = "dsfg"

    def test_validations(self):
        res = validate_env()
        self.assertTrue(res)

        del os.environ['AUTH0_USER_MANAGEMENT_CLIENT_ID']
        with self.assertRaises(api.ApiError) as e:
            validate_env()

        self.assertEqual("Env var AUTH0_USER_MANAGEMENT_CLIENT_ID required.", str(e.exception))


if __name__ == '__main__':
    import unittest

    unittest.main()
