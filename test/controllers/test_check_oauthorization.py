import os
import unittest

from werkzeug.exceptions import Forbidden

from test.controllers.utils import create_test_token
from xcube_hub.controllers.authorization import check_oauthorization, ApiEnvError, validate_scope_oauthorization
from xcube_hub.controllers.oauth import create_token


class TestOauthorization(unittest.TestCase):
    def setUp(self):
        self._claims = {
            "iss": "https://edc.eu.auth0.com/",
            "aud": ["https://test/api/v2"],
            "scope": ["manage:users", "manage:cubegens"],
            "gty": "client-credentials",
            "email": "test@mail.com",
            "permissions": ["manage:users", "manage:cubegens"]
        }

        self._claims, self._token = create_test_token(["manage:users", "manage:cubegens"])

    def test_check_oauthorization(self):
        expected = {'scopes': ["manage:users", "manage:cubegens"]}
        res = check_oauthorization(self._token)
        self.assertDictEqual(expected, res)

        token = create_token(claims=self._claims, days_valid=-1)

        with self.assertRaises(Forbidden) as e:
            check_oauthorization(token)

        self.assertEqual(403, e.exception.code)
        self.assertEqual("403 Forbidden: Signature has expired.", str(e.exception))

        os.environ['XCUBE_HUB_OAUTH_AUD'] = "https://test/api/v1"
        with self.assertRaises(Forbidden) as e:
            check_oauthorization(self._token)

        self.assertEqual(403, e.exception.code)
        self.assertEqual("403 Forbidden: Invalid audience", str(e.exception))

        del os.environ['XCUBE_HUB_OAUTH_AUD']
        with self.assertRaises(ApiEnvError) as e:
            check_oauthorization(self._token)

        self.assertEqual(500, e.exception.code)
        self.assertEqual("System error. Env var XCUBE_HUB_OAUTH_AUD must be given.", e.exception.description)

        os.environ['XCUBE_HUB_OAUTH_AUD'] = "https://test/api/v2"
        del os.environ['XCUBE_HUB_TOKEN_SECRET']

        with self.assertRaises(ApiEnvError) as e:
            check_oauthorization(self._token)

        self.assertEqual(500, e.exception.code)
        self.assertEqual("System error. Env var XCUBE_HUB_TOKEN_SECRET must be given.", e.exception.description)

    def test_validate_scope_oauthorization(self):
        required_scopes = ['a', ]
        token_scopes = ['a', 'b']
        res = validate_scope_oauthorization(required_scopes, token_scopes)
        self.assertTrue(res)

        token_scopes = ['c', 'b']
        res = validate_scope_oauthorization(required_scopes, token_scopes)
        self.assertFalse(res)


if __name__ == '__main__':
    unittest.main()
