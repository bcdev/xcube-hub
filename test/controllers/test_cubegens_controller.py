# coding: utf-8

from __future__ import absolute_import

import os
from typing import Dict
from unittest.mock import patch

from dotenv import load_dotenv

from test.controllers.utils import create_test_token
from test import BaseTestCase
import unittest

from xcube_hub import api
from xcube_hub.api import ApiError
from xcube_hub.core import cubegens
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

        self._claims, self._token = create_test_token(permissions=["manage:cubegens", ])
        self._headers = {'Authorization': f'Bearer {self._token}'}

        load_dotenv(dotenv_path='test/.env')
        K8sCfg.load_config_once()

    def tearDown(self) -> None:
        pass
        # cubegens.delete_all(self._user_id)
        # del_env(dotenv_path='test/.env')

    # @patch.object(BatchV1Api, 'list_namespaced_job', return_value=V1JobList(items=[]), create=True)
    @patch('xcube_hub.core.cubegens.list', return_value={}, create=True)
    def test_get_cubegens_controller(self, p):
        response = self.client.open('/api/v2/cubegens', headers=self._headers, method='GET')

        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual(0, len(response.json))

        p.side_effect = ApiError(400, 'test')
        response = self.client.open('/api/v2/cubegens', headers=self._headers, method='GET')

        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))

    @patch('xcube_hub.core.cubegens.get', return_value={}, create=True)
    def test_get_cubegen_controller(self, p):
        response = self.client.open('/api/v2/cubegens/test', headers=self._headers, method='GET')

        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual(0, len(response.json))

        p.side_effect = ApiError(400, message='test')
        response = self.client.open('/api/v2/cubegens/test', headers=self._headers, method='GET')

        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))

    @patch('xcube_hub.core.cubegens.info', return_value={}, create=True)
    def test_get_cubegen_info_controller(self, p):
        response = self.client.open('/api/v2/cubegens/info', headers=self._headers, json=self._cube_config.to_dict(),
                                    method='POST')

        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual(0, len(response.json))

        p.side_effect = ApiError(400, message='test')
        response = self.client.open('/api/v2/cubegens/info', headers=self._headers, json=self._cube_config.to_dict(),
                                    method='POST')

        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))

    @patch('xcube_hub.core.cubegens.delete_all', return_value={}, create=True)
    def test_delete_cubegens_controller(self, p):
        response = self.client.open('/api/v2/cubegens', headers=self._headers, method='DELETE')

        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

        p.side_effect = ApiError(400, message='test')
        response = self.client.open('/api/v2/cubegens', headers=self._headers, method='DELETE')

        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))

    @patch('xcube_hub.core.cubegens.delete_one', return_value={}, create=True)
    def test_delete_cubegen_controller(self, p):
        response = self.client.open('/api/v2/cubegens/test', headers=self._headers, method='DELETE')

        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

        p.side_effect = ApiError(400, message='test')
        response = self.client.open('/api/v2/cubegens/test', headers=self._headers, method='DELETE')

        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))

    @patch('xcube_hub.core.cubegens.create', return_value={}, create=True)
    def test_create_cubegen_controller(self, p):
        response = self.client.open('/api/v2/cubegens', headers=self._headers, json=self._cube_config.to_dict(), method='PUT')

        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

        p.side_effect = ApiError(400, message='test')
        response = self.client.open('/api/v2/cubegens', headers=self._headers, json=self._cube_config.to_dict(), method='PUT')

        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))

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
