# coding: utf-8

from __future__ import absolute_import

import os

import requests_mock
from flask import json
from xcube_hub.models.oauth_token import OauthToken
from test import BaseTestCase


@requests_mock.Mocker()
class TestOauthController(BaseTestCase):
    """OauthController integration test stubs"""

    def setUp(self):
        os.environ['XCUBE_HUB_OAUTH_AUD'] = 'https://test'
        os.environ['AUTH0_USER_MANAGEMENT_CLIENT_ID'] = 'asdc'
        os.environ['AUTH0_USER_MANAGEMENT_CLIENT_SECRET'] = 'asdc'
        os.environ['XCUBE_HUB_TOKEN_SECRET'] = '+k5kLdMEX1o0pfYZlieAIjKeqAW0wh+5l9PfReyoKyZqYndb2MeYH' \
                                               'XGqqZ2Uh1zZATCHMwgyIirYSVDAi9N6izWBYAG/GGfS3VJFA2FEg+' \
                                               'YMQSHbhCTdG+/7p7XvltFyO8MPLhU5LFDWLc2rZCOliSBocfnYrM5A' \
                                               'aHD7JsjUqR+Ej3vVcfWAHPAyp66m/1TaD6svCuDcdXN09I0UJ+10Q/P' \
                                               's2Vz9qHKhK6oW8gqXHjG8+jZvjjeH29LLkPdYHM5nofyDMumJYRrHBu' \
                                               'RcnCt4EtDUJurH4LizPCvrAbMarc/03w1+vu+LEpRR67O7N7zda' \
                                               'XBkPc4VRwF5aLCh5MLeEg=='

    def test_oauth_token_post(self, m):
        """Test case for oauth_token_post

        Get authorization token
        """
        m.post("https://edc.eu.auth0.com/oauth/token", json={'access_token': 'sdfvdfv'})
        m.get('https://edc.eu.auth0.com/api/v2/users', json=[{'user_id': 'auth0fred', 'email': 'bla'}])
        m.get(f"https://edc.eu.auth0.com/api/v2/users/auth0fred/permissions", json=[{'permission_name': 'test_1'}, ])

        body = OauthToken(client_id='abc', client_secret='def', audience='https://test', user_name='df',
                          grant_type='client-credentials')

        response = self.client.open('/api/v2/oauth/token', method='POST', data=json.dumps(body),
                                    content_type='application/json')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

        response = self.client.open('/api/v2/oauth/token', method='POST', data=json.dumps(body),
                                    content_type='application/csv')
        self.assert_status(response, 415, 'Response body is : ' + response.data.decode('utf-8'))

        del os.environ['XCUBE_HUB_OAUTH_AUD']
        response = self.client.open('/api/v2/oauth/token', method='POST', data=json.dumps(body),
                                    content_type='application/json')

        data = response.json
        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual("Env var XCUBE_HUB_OAUTH_AUD must be set", data['message'])


if __name__ == '__main__':
    import unittest

    unittest.main()
