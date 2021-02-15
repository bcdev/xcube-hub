# coding: utf-8

from __future__ import absolute_import

from flask import json
from xcube_hub.models.o_auth_token import OAuthToken  # noqa: E501
from test import BaseTestCase


class TestOauthController(BaseTestCase):
    """OauthController integration test stubs"""

    def test_oauth_token_post(self):
        """Test case for oauth_token_post

        Get authorization token
        """
        body = OAuthToken()
        response = self.client.open(
            '/api/v2/oauth/token',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
