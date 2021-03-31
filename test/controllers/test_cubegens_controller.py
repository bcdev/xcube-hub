# coding: utf-8

from __future__ import absolute_import

import os
from typing import Dict
from unittest import mock

from dotenv import load_dotenv

from test.controllers.utils import create_test_token
from test import BaseTestCase
import unittest

from xcube_hub import api
from xcube_hub.core import cubegens
from xcube_hub.core.validations import validate_env
from xcube_hub.k8scfg import K8sCfg
from xcube_hub.models.cubegen_config import CubegenConfig
from xcube_hub.typedefs import JsonObject


def create_cubegen2s(body: JsonObject, token_info: Dict):
    print("Hello")
    raise api.ApiError(400, "")


CUBEGEN_TEST = {
    "input_configs": [
        {
            "store_id": "@sentinelhub_codede",
            "data_id": "S3OLCI",
            "open_params": {
                "tile_size": [
                    1000,
                    1000
                ]
            }
        }
    ],
    "cube_config": {
        "variable_names": [
            "B01"
        ],
        "crs": "http://www.opengis.net/def/crs/EPSG/0/4326",
        "spatial_res": 0.01,
        "bbox": [
            -180,
            -85,
            180,
            85
        ],
        "time_range": [
            "2016-04-17",
            "2016-04-20"
        ],
        "time_period": "1D"
    },
    "output_config": {
        "store_id": "s3",
        "store_params": {
            "bucket_name": "eurodatacube-test",
        }
    }
}

TEST_CLAIMS = {
    "iss": "https://edc.eu.auth0.com/",
    "aud": 'https://test',
    "scope": ['manage:callbacks', ],
    "gty": "client-credentials",
    "email": 'heinrich@gmail.com',
    "permissions": ['manage:callbacks', ]
}


@unittest.skipIf(os.getenv("UNITTESTS_SKIP_K8s", "0") == "1", "Kubernetes skipped")
class TestCubeGensController(BaseTestCase):
    """CubeGensController integration test stubs"""

    def setUp(self) -> None:
        self._user_id = "a97dfebf4098c0f5c16bca61e2b76c373"
        self._claims, self._token = create_test_token()
        self._cube_config = CubegenConfig.from_dict(CUBEGEN_TEST)
        load_dotenv(dotenv_path='test/.env')
        validate_env()
        K8sCfg.load_config_once()

    def tearDown(self) -> None:
        cubegens.delete_all(self._user_id)

    @mock.patch('xcube_hub.controllers.cubegens.create_cubegen', side_effect=create_cubegen2s)
    def test_create_cubegen(self, m):
        """Test case for create_cubegen

        Create a cubegen
        """
        response = self.client.open(
            '/api/v2/cubegens',
            method='PUT',
            json=self._cube_config.to_dict(),
            headers={'Authorization': f"Bearer {self._token}"},
            content_type='application/json')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_cubegen(self):
        """Test case for delete_cubegen

        Delete a cubegen
        """

        res = cubegens.create("a97dfebf4098c0f5c16bca61e2b76c373", email="richard@mail.com", cfg=CUBEGEN_TEST, token=self._token)
        response = self.client.open(f'/api/v2/cubegens/{res["cubegen_id"]}',
                                    headers={'Authorization': f"Bearer {self._token}"}, method='DELETE')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_cubegens(self):
        """Test case for delete_cubegens

        Delete all cubegens
        """
        cubegens.create("a97dfebf4098c0f5c16bca61e2b76c373", email="richard@mail.com", cfg=CUBEGEN_TEST, token=self._token)
        response = self.client.open('/api/v2/cubegens', headers={'Authorization': f"Bearer {self._token}"},
                                    method='DELETE')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

    def test_get_costs(self):
        """Test case for get_costs

        Receive cost information for running a cubegen
        """
        response = self.client.open(
            '/api/v2/cubegens/info',
            method='POST',
            json=CUBEGEN_TEST,
            headers={'Authorization': f"Bearer {self._token}"},
            content_type='application/json')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

    def test_get_cubegen(self):
        """Test case for get_cubegen

        List specific cubegen
        """
        res = cubegens.create("a97dfebf4098c0f5c16bca61e2b76c373", email="richard@mail.com", cfg=CUBEGEN_TEST, token=self._token)
        response = self.client.open(f'/api/v2/cubegens/{res["cubegen_id"]}',
                                    headers={'Authorization': f"Bearer {self._token}"}, method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_cubegens(self):
        """Test case for get_cubegens

        List cubegens
        """
        cubegens.create("a97dfebf4098c0f5c16bca61e2b76c373", email="richard@mail.com", cfg=CUBEGEN_TEST, token=self._token)
        response = self.client.open('/api/v2/cubegens', headers={'Authorization': f"Bearer {self._token}"},
                                    method='GET')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest

    unittest.main()
