# coding: utf-8

from __future__ import absolute_import

import os

import requests_mock
from test import BaseTestCase

TEST_POOLS = {'result': {'cciodp': {'description': 'Data from the ESA CCI Open Data Portal API', 'store_id': 'cciodp',
                                    'title': 'ESA Climate Change Initiative (CCI)'},
                         'cds': {'description': 'Selected datasets from the Copernicus CDS API', 'store_id': 'cds',
                                 'title': 'C3S Climate Data Store (CDS)'}}}


@requests_mock.Mocker()
class TestOauthController(BaseTestCase):
    """OauthController integration test stubs"""

    def setUp(self):
        os.environ['XCUBE_GEN_DATA_POOLS_PATH'] = 'test/resources/data-pools.yaml'

    def test_get_stores(self, m):
        """Test case for oauth_token_post

        Get authorization token
        """

        response = self.client.open('/api/v2/stores', method='GET')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))
        self.assertDictEqual(TEST_POOLS, response.json)


if __name__ == '__main__':
    import unittest

    unittest.main()
