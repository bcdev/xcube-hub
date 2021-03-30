# coding: utf-8

from __future__ import absolute_import

import os

import requests_mock
from test import BaseTestCase

TEST_POOLS = {'sentinelhub_codede': {'title': 'SENTINEL Hub (Central Europe)', 'store_id': 'sentinelhub',
                                     'cost_params': {'scheme': 'punits', 'input_pixels_per_punit': 262144,
                                                     'input_punits_weight': 1.0, 'output_pixels_per_punit': 262144,
                                                     'output_punits_weight': 1.0},
                                     'store_params': {'api_url': 'https://services.sentinel-hub.com'}}}


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
