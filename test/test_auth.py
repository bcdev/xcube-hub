import os
import unittest
from unittest.mock import patch
from xcube_hub import api
from xcube_hub.auth0 import Auth0
from xcube_hub.service import new_app
from dotenv import load_dotenv
from flask_testing import TestCase


class TestAuth(TestCase):
    def create_app(self) -> None:
        load_dotenv()
        os.environ["XCUBE_GEN_API_RUN_LOCAL"] = '1'
        app = new_app()
        return app

    def test_auth0(self):
        res = self.client.get('/')
        self.assertEqual(200, res.status_code, False)

    def test_raise_for_invalid_user(self):
        user_id = 'a4b7f0554c1a5b2085c5ae0513b49cc04'
        mock_token_auth_patch = patch('xcube_hub.auth0.Auth0.get_token_auth_header')
        mock_tocken_auth = mock_token_auth_patch.start()
        mock_tocken_auth.return_value = "akuicvgkasduczgdkauscgkauscdz"

        mock_headers_patcher = patch('jose.jwt.get_unverified_claims')
        mock_headers = mock_headers_patcher.start()
        mock_headers.return_value = {}

        mock_get_patch = patch('xcube_hub.auth0.Auth0._get_user_info_from_auth0')
        mock_get = mock_get_patch.start()
        mock_get.return_value = {'name': 'Tom.Jones@brockmann-consult.de'}

        res = Auth0.raise_for_invalid_user_id(user_id)
        self.assertTrue(res)

        user_id = 'hacking'
        with self.assertRaises(api.ApiError) as e:
            Auth0.raise_for_invalid_user_id(user_id)

        self.assertEqual("access denied: Insufficient privileges for this operation.",
                         str(e.exception))

        mock_get.return_value = {'nam': 'Tom.Jones@brockmann-consult.de'}
        with self.assertRaises(api.ApiError) as e:
            Auth0.raise_for_invalid_user_id(user_id)

        self.assertEqual("access denied: Could not read name from user info.",
                         str(e.exception))

        mock_token_auth_patch.stop()
        mock_headers_patcher.stop()
        mock_get_patch.stop()

    def test_raise_for_invalid_user_when_m2m(self):
        mock_token_auth_patch = patch('xcube_hub.auth0.Auth0.get_token_auth_header')
        mock_tocken_auth = mock_token_auth_patch.start()
        mock_tocken_auth.return_value = "akuicvgkasduczgdkauscgkauscdz"

        mock_headers_patcher = patch('jose.jwt.get_unverified_claims')
        mock_headers = mock_headers_patcher.start()
        mock_headers.return_value = {'gty': 'client-credentials'}

        user_id = 'hacking'
        res = Auth0.raise_for_invalid_user_id(user_id)
        self.assertTrue(res)

        mock_headers.return_value = {'qty': 'client-credential'}
        with self.assertRaises(api.ApiError) as e:
            Auth0.raise_for_invalid_user_id(user_id)

        self.assertEqual("Unauthorized", str(e.exception))

        mock_token_auth_patch.stop()
        mock_headers_patcher.stop()


if __name__ == '__main__':
    unittest.main()
