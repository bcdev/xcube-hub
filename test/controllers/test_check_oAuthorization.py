import os
import unittest

from werkzeug.exceptions import Forbidden

from xcube_hub.controllers.authorization import check_oAuthorization, ApiEnvError, validate_scope_oAuthorization
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

        os.environ['XCUBE_HUB_TOKEN_SECRET'] = '+k5kLdMEX1o0pfYZlieAIjKeqAW0wh+5l9PfReyoKyZqYndb2MeYHXGqqZ2Uh1zZATCHMwgyIirYSVDAi9N6izWBYAG/GGfS3VJFA2FEg+YMQSHbhCTdG+/7p7XvltFyO8MPLhU5LFDWLc2rZCOliSBocfnYrM5AaHD7JsjUqR+Ej3vVcfWAHPAyp66m/1TaD6svCuDcdXN09I0UJ+10Q/Ps2Vz9qHKhK6oW8gqXHjG8+jZvjjeH29LLkPdYHM5nofyDMumJYRrHBuRcnCt4EtDUJurH4LizPCvrAbMarc/03w1+vu+LEpRR67O7N7zdaXBkPc4VRwF5aLCh5MLeEg==]'
        os.environ['XCUBE_HUB_OAUTH_AUD'] = "https://test/api/v2"
        self._token = create_token(claims=self._claims)

    def test_check_oAuthorization(self):
        expected = {'scopes': ["manage:users", "manage:cubegens"], 'email': "test@mail.com"}
        res = check_oAuthorization(self._token)
        self.assertEqual(expected, res)

        token = create_token(claims=self._claims, days_valid=-1)

        with self.assertRaises(Forbidden) as e:
            check_oAuthorization(token)

        self.assertEqual(403, e.exception.code)
        self.assertEqual("403 Forbidden: Signature has expired.", str(e.exception))

        os.environ['XCUBE_HUB_OAUTH_AUD'] = "https://test/api/v1"
        with self.assertRaises(Forbidden) as e:
            check_oAuthorization(self._token)

        self.assertEqual(403, e.exception.code)
        self.assertEqual("403 Forbidden: Invalid audience", str(e.exception))

        del os.environ['XCUBE_HUB_OAUTH_AUD']
        with self.assertRaises(ApiEnvError) as e:
            check_oAuthorization(self._token)

        self.assertEqual(500, e.exception.code)
        self.assertEqual("System error. Env var XCUBE_HUB_OAUTH_AUD must be given.", e.exception.description)

        os.environ['XCUBE_HUB_OAUTH_AUD'] = "https://test/api/v2"
        del os.environ['XCUBE_HUB_TOKEN_SECRET']

        with self.assertRaises(ApiEnvError) as e:
            check_oAuthorization(self._token)

        self.assertEqual(500, e.exception.code)
        self.assertEqual("System error. Env var XCUBE_HUB_TOKEN_SECRET must be given.", e.exception.description)

    def test_validate_scope_oAuthorization(self):
        required_scopes = ['a', ]
        token_scopes = ['a', 'b']
        res = validate_scope_oAuthorization(required_scopes, token_scopes)
        self.assertTrue(res)

        token_scopes = ['c', 'b']
        res = validate_scope_oAuthorization(required_scopes, token_scopes)
        self.assertFalse(res)


if __name__ == '__main__':
    unittest.main()
