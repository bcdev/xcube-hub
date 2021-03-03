import os
import unittest

from dotenv import load_dotenv
from werkzeug.exceptions import Unauthorized, Forbidden

# noinspection PyProtectedMember
from xcube_hub.auth import Auth, _AuthXcube, _Auth0, _AuthMocker


class TestAuth(unittest.TestCase):
    def setUp(self):
        load_dotenv(dotenv_path='test/.env')

    def test_auth(self):
        auth = Auth(provider='xcube')
        self.assertIsInstance(auth._provider, _AuthXcube)

        auth = Auth(provider='auth0')
        self.assertIsInstance(auth._provider, _Auth0)

        auth = Auth(provider='mocker')
        self.assertIsInstance(auth._provider, _AuthMocker)

        with self.assertRaises(Unauthorized) as e:
            Auth(provider='auth')

        self.assertEqual("401 Unauthorized: Provider auth unknown.", str(e.exception))

    def test_instance(self):
        auth = Auth.instance(iss="https://xcube-gen.brockmann-consult.de/", refresh=True)
        self.assertIsInstance(auth, Auth)
        self.assertIsInstance(auth._provider, _AuthXcube)

        auth = Auth.instance(iss="https://test/")
        self.assertIsInstance(auth, Auth)
        self.assertIsInstance(auth._provider, _AuthXcube)

        Auth._instance = None
        auth = Auth.instance(iss="https://edc.eu.auth0.com/")
        self.assertIsInstance(auth, Auth)
        self.assertIsInstance(auth._provider, _Auth0)

        auth = Auth.instance(iss="https://test/", refresh=True)
        self.assertIsInstance(auth, Auth)
        self.assertIsInstance(auth._provider, _AuthMocker)

        with self.assertRaises(Unauthorized) as e:
            Auth.instance(iss="https://xcube-geodb.brockmann-consult.de/", refresh=True)

        self.assertEqual("401 Unauthorized: Issuer https://xcube-geodb.brockmann-consult.de/ unknown.", str(e.exception))

    def test_verify_token(self):
        auth = Auth.instance(iss="https://test/", refresh=True)

        with self.assertRaises(Forbidden) as e:
            auth.verify_token('dfsbsdfb')

        self.assertEqual("403 Forbidden: Access denied. Invalid claims.", str(e.exception))

    def test_permissions(self):
        auth = Auth.instance(iss="https://test/", refresh=True)
        auth._claims = {'aud': "https://test/", "permissions": ["manage:test", ]}

        permissions = auth.permissions
        self.assertEqual(["manage:test", ], permissions)

        auth._claims = []
        permissions = auth.permissions
            
        self.assertEqual([], permissions)

        auth._claims = {'aud': "https://test/", "scope": "manage:test manage:test2"}
        permissions = auth.permissions

        self.assertEqual(["manage:test", "manage:test2"], permissions)

    def test_email(self):
        auth = Auth.instance(iss="https://test/", refresh=True)

        email = auth.email
        self.assertEqual("mocker@mail.nz", email)

    def test_user_id(self):
        auth = Auth.instance(iss="https://test/", refresh=True)

        user_id = auth.user_id
        self.assertEqual("afc97cfc3e4dc541495e84bbb78804dfc", user_id)

    def test_auth0(self):
        auth = Auth.instance(iss="https://edc.eu.auth0.com/", refresh=True)
        self.assertEqual('edc.eu.auth0.com', auth._provider._domain)
        self.assertEqual("https://xcube-gen.brockmann-consult.de/api/v2/", auth._provider._audience)
        self.assertEqual(["RS256"], auth._provider._algorithms)

        domain = os.getenv('AUTH0_DOMAIN')
        del os.environ['AUTH0_DOMAIN']
        with self.assertRaises(Unauthorized) as e:
            auth = Auth.instance(iss="https://edc.eu.auth0.com/", refresh=True)

        self.assertEqual("401 Unauthorized: Auth0 error: Domain not set", str(e.exception))

        os.environ['AUTH0_DOMAIN'] = domain

        audience = os.getenv('XCUBE_HUB_OAUTH_AUD')
        del os.environ['XCUBE_HUB_OAUTH_AUD']

        with self.assertRaises(Unauthorized) as e:
            auth = Auth.instance(iss="https://edc.eu.auth0.com/", refresh=True)

        self.assertEqual("401 Unauthorized: Auth0 error: Audience not set", str(e.exception))

        os.environ['XCUBE_HUB_OAUTH_AUD'] = audience

    def test_auth0_email(self):
        auth = Auth.instance(iss="https://edc.eu.auth0.com/", refresh=True)
        auth._claims = {'https://xcube-gen.brockmann-consult.de/user_email': 'mock@mail.nz'}

        email = auth.email
        self.assertEqual('mock@mail.nz', email)

        auth._claims = {'https://xcube-gen.brockmann-consult.de/mail': 'mock@mail.nz'}

        with self.assertRaises(Unauthorized) as e:
            email = auth.email
        self.assertEqual('401 Unauthorized: Access denied. Cannot get email.', str(e.exception))

    def test_xcube_email(self):
        auth = Auth.instance(iss="https://xcube-gen.brockmann-consult.de/", refresh=True)
        auth._claims = {'email': 'mock@mail.nz'}

        email = auth.email
        self.assertEqual('mock@mail.nz', email)

        auth._claims = {'https://xcube-gen.brockmann-consult.de/user_email': 'mock@mail.nz'}

        with self.assertRaises(Unauthorized) as e:
            email = auth.email
        self.assertEqual('401 Unauthorized: Access denied. Cannot get email from token.', str(e.exception))

    def test_verification_xcube(self):
        auth = Auth.instance(iss="https://xcube-gen.brockmann-consult.de/", refresh=True)

        with self.assertRaises(Unauthorized) as e:
            token = auth.verify_token(token="fvdfv")

        self.assertEqual("401 Unauthorized: Not enough segments", str(e.exception))

    def test_verification_auth0(self):
        auth = Auth.instance(iss="https://edc.eu.auth0.com/", refresh=True)

        with self.assertRaises(Unauthorized) as e:
            token = auth.verify_token(token="fvdfv")

        self.assertEqual("401 Unauthorized: invalid_header: Invalid header. Use an RS256 signed JWT Access Token",
                         str(e.exception))


if __name__ == '__main__':
    unittest.main()
