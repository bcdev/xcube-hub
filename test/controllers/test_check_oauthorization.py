import unittest

from werkzeug.exceptions import Forbidden

from test.controllers.utils import create_test_token
from xcube_hub.controllers.authorization import check_oauthorization, validate_scope_oauthorization
from xcube_hub.controllers.oauth import create_token


class TestOauthorization(unittest.TestCase):
    def setUp(self):
        self._claims, self._token = create_test_token(["manage:users", "manage:cubegens"])

        self._claims, self._token = create_test_token(["manage:users", "manage:cubegens"])

    def test_check_oauthorization(self):
        expected = {'scopes': ['manage:users', 'manage:cubegens'], 'user_id': 'a97dfebf4098c0f5c16bca61e2b76c373',
                    'email': 'test@mail.com'}
        res = check_oauthorization(self._token)
        self.assertDictEqual(expected, res)

        token = create_token(claims=self._claims, days_valid=-1)

        with self.assertRaises(Forbidden) as e:
            check_oauthorization(token)

        self.assertEqual(403, e.exception.code)
        self.assertEqual("403 Forbidden: Signature has expired.", str(e.exception))

        claims, token = create_test_token(["manage:users", "manage:cubegens"], "https://test/api/v3")
        with self.assertRaises(Forbidden) as e:
            check_oauthorization(token)

        self.assertEqual(403, e.exception.code)
        self.assertEqual("403 Forbidden: Invalid audience", str(e.exception))

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
