# coding: utf-8

from __future__ import absolute_import

import os

import requests_mock
from dotenv import load_dotenv
from flask import json

from test.controllers.utils import del_env
from xcube_hub.models.oauth_token import OauthToken
from test import BaseTestCase


@requests_mock.Mocker()
class TestOauthController(BaseTestCase):
    """OauthController integration test stubs"""

    def setUp(self):
        load_dotenv(dotenv_path='test/.env')

    def tearDown(self) -> None:
        del_env(dotenv_path='test/.env')

    def test_oauth_token_post(self, m):
        """Test case for oauth_token_post

        Get authorization token
        """
        m.post("https://edc.eu.auth0.com/oauth/token", json={'access_token': 'sdfvdfv'})
        m.get('https://edc.eu.auth0.com/api/v2/users', json=[{'user_id': 'auth0fred', 'email': 'bla'}])
        m.get(f"https://edc.eu.auth0.com/api/v2/users/auth0fred/permissions", json=[{'permission_name': 'test_1'}, ])

        body = OauthToken(client_id='abc', client_secret='def', audience='https://test',
                          grant_type='client-credentials')

        response = self.client.open('/api/v2/oauth/token', method='POST', data=json.dumps(body),
                                    content_type='application/json')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

        response = self.client.open('/api/v2/oauth/token', method='POST', data=json.dumps(body),
                                    content_type='application/csv')
        self.assert_status(response, 415, 'Response body is : ' + response.data.decode('utf-8'))

        aud = os.environ['XCUBE_HUB_OAUTH_AUD']
        del os.environ['XCUBE_HUB_OAUTH_AUD']
        response = self.client.open('/api/v2/oauth/token', method='POST', data=json.dumps(body),
                                    content_type='application/json')

        data = response.json
        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual("Environment Variable XCUBE_HUB_OAUTH_AUD does not exist.", data['message'])

        os.environ['XCUBE_HUB_OAUTH_AUD'] = aud
        secret = os.environ['XCUBE_HUB_OAUTH_HS256_SECRET']
        os.environ['XCUBE_HUB_OAUTH_HS256_SECRET'] = 'sdfvgd'
        response = self.client.open('/api/v2/oauth/token', method='POST', data=json.dumps(body),
                                    content_type='application/json')

        os.environ['XCUBE_HUB_OAUTH_HS256_SECRET'] = secret
        data = response.json
        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual("System Error: Invalid token secret given.", data['message'])


if __name__ == '__main__':
    import unittest

    unittest.main()
