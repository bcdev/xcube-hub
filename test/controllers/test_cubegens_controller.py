# coding: utf-8

from __future__ import absolute_import

import io
import json
from unittest.mock import patch

from werkzeug.datastructures import FileStorage

from test import BaseTestCase

from xcube_hub import api
from xcube_hub.api import ApiError
from xcube_hub.controllers import cubegens


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


CUBEGEN_TEST_MULTI_PART = {
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


class TestCubeGensController(BaseTestCase):
    """CubeGensController integration test stubs"""

    def tearDown(self) -> None:
        pass
        # cubegens.delete_all(self._user_id)
        # del_env(dotenv_path='test/.env')

    # @patch.object(BatchV1Api, 'list_namespaced_job', return_value=V1JobList(items=[]), create=True)
    # @patch('xcube_hub.core.cubegens.list', return_value={}, create=True)
    # def test_get_cubegens_controller(self, p):
    #     response = self.client.open('/api/v2/cubegens', headers=self._headers, method='GET')
    #
    #     self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))
    #     self.assertEqual(0, len(response.json))
    #
    #     p.side_effect = ApiError(400, 'test')
    #     response = self.client.open('/api/v2/cubegens', headers=self._headers, method='GET')
    #
    #     self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))
    #
    # @patch('xcube_hub.core.cubegens.get', return_value={}, create=True)
    # def test_get_cubegen_controller(self, p):
    #     response = self.client.open('/api/v2/cubegens/test', headers=self._headers, method='GET')
    #
    #     self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))
    #     self.assertEqual(0, len(response.json))
    #
    #     p.side_effect = ApiError(400, message='test')
    #     response = self.client.open('/api/v2/cubegens/test', headers=self._headers, method='GET')
    #
    #     self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))
    #
    # @patch('xcube_hub.core.cubegens.info', return_value={}, create=True)
    # def test_get_cubegen_info_controller(self, p):
    #     response = self.client.open('/api/v2/cubegens/info', headers=self._headers, json=self._cube_config.to_dict(),
    #                                 method='POST')
    #
    #     self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))
    #     self.assertEqual(0, len(response.json))
    #
    #     p.side_effect = ApiError(400, message='test')
    #     response = self.client.open('/api/v2/cubegens/info', headers=self._headers, json=self._cube_config.to_dict(),
    #                                 method='POST')
    #
    #     self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))
    #
    # @patch('xcube_hub.core.cubegens.delete_all', return_value={}, create=True)
    # def test_delete_cubegens_controller(self, p):
    #     response = self.client.open('/api/v2/cubegens', headers=self._headers, method='DELETE')
    #
    #     self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))
    #
    #     p.side_effect = ApiError(400, message='test')
    #     response = self.client.open('/api/v2/cubegens', headers=self._headers, method='DELETE')
    #
    #     self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))
    #
    # @patch('xcube_hub.core.cubegens.delete_one', return_value={}, create=True)
    # def test_delete_cubegen_controller(self, p):
    #     response = self.client.open('/api/v2/cubegens/test', headers=self._headers, method='DELETE')
    #
    #     self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))
    #
    #     p.side_effect = ApiError(400, message='test')
    #     response = self.client.open('/api/v2/cubegens/test', headers=self._headers, method='DELETE')
    #
    #     self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))

    @patch('xcube_hub.core.cubegens.process_user_code', create=True)
    @patch('xcube_hub.core.cubegens.create', return_value={'cubegen_id': 'ajob_id', 'status': 'ready'}, create=True)
    def test_create_cubegen_controller(self, p, process):
        cfg = {
            "input_configs": [
                {
                    "store_id": "@test",
                    "data_id": "DATASET-1.zarr"
                }
            ],
            "cube_config": {
            },
            "code_config": {
                "file_set": {
                    "path": ""
                },
                "callable_ref": "processor:process_dataset",
                "callable_params": {
                    "output_var_name": "X",
                    "input_var_name_1": "A",
                    "input_var_name_2": "B",
                    "factor_1": 0.4,
                    "factor_2": 0.2
                }
            },
            "output_config": {
                "store_id": "@test",
                "data_id": "OUTPUT.zarr",
                "replace": True
            }
        }

        cfg_json = json.dumps(cfg)

        cfg = io.BytesIO(cfg_json.encode('UTF-8'))
        cfg = FileStorage(filename='test.json', stream=cfg)

        expected = {'cubegen_id': 'ajob_id', 'status': 'ready'}
        p.return_value = expected

        res = cubegens.create_cubegen(body=cfg, token_info={'user_id': 'drwho', 'email': 'drwho@mail', 'token': 'abc'})
        self.assertDictEqual(expected, res[0])
        self.assertEqual(200, res[1])

        p.side_effect = ApiError(400, message='error')

        cfg = io.BytesIO(cfg_json.encode('UTF-8'))
        cfg = FileStorage(filename='test.json', stream=cfg)

        res = cubegens.create_cubegen(body=cfg, token_info={'user_id': 'drwho', 'email': 'drwho@mail', 'token': 'abc'})
        self.assertEqual('error', res[0]['message'])
        self.assertGreater(len(res[0]['traceback']), 0)
        self.assertEqual(400, res[1])

    @patch('xcube_hub.core.cubegens.delete_one', return_value={'cubegen_id': 'ajob_id', 'status': 'ready'}, create=True)
    def test_delete_cubegen(self, p):
        """Test case for delete_cubegen

        Delete a cubegen
        """

        res = cubegens.delete_cubegen(cubegen_id='anid')

        self.assertEqual(200, res[1])

        p.side_effect = api.ApiError(400, 'Error')

        res = cubegens.delete_cubegen(cubegen_id='anid')

        self.assertEqual(400, res[1])
        self.assertEqual('Error', res[0]['message'])

    @patch('xcube_hub.core.cubegens.delete_all', return_value='SUCCESS', create=True)
    def test_delete_cubegens(self, p):
        """Test case for delete_cubegen

        Delete a cubegen
        """

        res = cubegens.delete_cubegens(token_info={'user_id': 'drwho'})

        self.assertEqual(200, res[1])

        p.side_effect = api.ApiError(400, 'Error')

        res = cubegens.delete_cubegens(token_info={'user_id': 'drwho'})

        self.assertEqual(400, res[1])
        self.assertEqual('Error', res[0]['message'])

    @patch('xcube_hub.core.cubegens.info', create=True)
    def test_get_cubegen_info(self, p):
        """Test case for delete_cubegen

        Delete a cubegen
        """

        p.return_value = dict(dataset_descriptor={}, size_estimation={}, cost_estimation={})

        res = cubegens.get_cubegen_info(body={}, token_info={'user_id': 'drwho',
                                                             'email': 'drwho@bbc.org',
                                                             'token': 'dscsdc'})

        self.assertEqual(200, res[1])

        p.side_effect = api.ApiError(400, 'Error')

        res = cubegens.get_cubegen_info(body={}, token_info={'user_id': 'drwho',
                                                             'email': 'drwho@bbc.org',
                                                             'token': 'dscsdc'})

        self.assertEqual(400, res[1])
        self.assertEqual('Error', res[0]['message'])

    @patch('xcube_hub.core.cubegens.get', create=True)
    def test_get_cubegen(self, p):
        """Test case for delete_cubegen

        Delete a cubegen
        """

        p.return_value = {'cubegen_id': 'anid', 'status': 'ready', 'output': [], 'progress': 100}

        res = cubegens.get_cubegen(cubegen_id='anid', token_info={'user_id': 'drwho'})

        self.assertEqual(200, res[1])

        p.side_effect = api.ApiError(400, 'Error')

        res = cubegens.get_cubegen(cubegen_id='anid', token_info={'user_id': 'drwho'})

        self.assertEqual(400, res[1])
        self.assertEqual('Error', res[0]['message'])

    @patch('xcube_hub.core.cubegens.list', create=True)
    def test_get_cubegens(self, p):
        """Test case for delete_cubegen

        Delete a cubegen
        """

        p.return_value = []

        res = cubegens.get_cubegens(token_info={'user_id': 'drwho'})

        self.assertEqual(200, res[1])

        p.side_effect = api.ApiError(400, 'Error')

        res = cubegens.get_cubegens(token_info={'user_id': 'drwho'})

        self.assertEqual(400, res[1])
        self.assertEqual('Error', res[0]['message'])


if __name__ == '__main__':
    import unittest

    unittest.main()
