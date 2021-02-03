import hashlib
import json
import unittest
from unittest.mock import patch
import os

import boto3
import moto

from test.config import SH_CFG
from test.setup_utils import set_env
from xcube_hub import api
from xcube_hub.controllers.callback import get_callback, put_callback, delete_callback
from xcube_hub.controllers.users import add_processing_units
from xcube_hub.keyvaluedatabase import KeyValueDatabase
from xcube_hub.service import new_app

KeyValueDatabase.use_mocker = True

CFG = {
    "input_configs": [
        {
            "store_id": "@sentinelhub_codede",
            "data_id": "S2L1C",
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
        "spatial_res": 0.001,
        "bbox": [
            -6.635742187500001,
            6.489983332670651,
            -5.185546875000001,
            7.27529233637217
        ],
        "time_range": [
            "2015-11-01",
            "2015-11-04"
        ],
        "time_period": "1D"
    },
    "output_config": {
        "store_id": "s3",
        "store_params": {
            "bucket_name": "eurodatacube-test"
        }
    }
}

class TestCallback(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["XCUBE_GEN_API_RUN_LOCAL"] = '1'
        self._access_token = {'access_token': "sdfvsdvdsfv"}
        self._app = new_app()
        self._client = self._app.test_client()
        self._client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer ' + self._access_token['access_token']
        self._sh_config = SH_CFG
        set_env()

    def test_get_callback(self):
        expected = {
            'message': 'bla',
            'status': 'ERROR'
        }

        mock_get_patch = patch('xcube_hub.keyvaluedatabase.KeyValueDatabase.get')
        mock_get = mock_get_patch.start()
        mock_get.return_value = json.dumps(expected)

        res = get_callback('user2', 'job3')
        self.assertTrue(res)

        mock_get.return_value = None
        with self.assertRaises(api.ApiError) as e:
            get_callback('user2', 'job3')

        self.assertEqual('Could not find any callback entries for that key.', str(e.exception))
        self.assertEqual(404, e.exception.status_code)

        mock_get_patch.stop()

    # noinspection InsecureHash
    def test_put_callback(self):
        with moto.mock_s3():
            mock_get_patch = patch('xcube_hub.auth0.Auth0.get_token_auth_header')
            mock_get = mock_get_patch.start()
            mock_get.return_value = "dsvdfsvdsvfdsvdsvdsv"

            mock_get2_patch = patch('xcube_hub.auth0.Auth0.get_user_info_from_auth0')
            mock_get2 = mock_get2_patch.start()
            mock_get2.return_value = {'name': "heinrich"}

            s3 = boto3.client('s3')
            s3.create_bucket(Bucket='eurodatacube', CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
            user_name = 'heinrich'
            user_id = hashlib.md5(user_name.encode('utf-8')).hexdigest()

            punits_request_1 = dict(punits=dict(total_count=1000000,
                                                user_name=user_name,
                                                price_amount=200,
                                                price_currency='€'))

            add_processing_units('heinrich', punits_request_1)

            punits = {
                'schema': {
                    'dims': {
                        'time': 1177,
                        'y': 2048,
                        'x': 2048
                    },
                    'image_size': [2048, 2048],
                    'tile_size': [1024, 1024],
                    'num_variables': 2,
                    'num_tiles': [2, 2],
                    'num_requests': 9416,
                    'num_bytes': 39493566464
                },
                'punits': {
                    'input_count': 37664,
                    'input_weight': 1.0,
                    'output_count': 37664,
                    'output_weight': 1.0,
                    'total_count': 37664
                }
            }

            expected = {
                "state": {"error": False},
                "sender": "on_end",
                "message": punits
            }

            kvdb = KeyValueDatabase.instance()
            kvdb.set(user_id + '__job3__cfg', CFG)
            res = put_callback(user_id='620698091bdd62d3dc05d58c2db07939', job_id='job3', value=expected)

            self.assertTrue(res)

            mock_get_patch.stop()
            mock_get2_patch.stop()

    def test_delete_callback(self):
        mock_delete_patch = patch('xcube_hub.keyvaluedatabase.KeyValueDatabase.delete')
        mock_delete = mock_delete_patch.start()
        mock_delete.return_value = 1

        res = delete_callback(user_id='user2', job_id='job3')
        self.assertEqual(1, res)

        mock_delete.return_value = 0
        with self.assertRaises(api.ApiError) as e:
            delete_callback(user_id='user2', job_id='job3')

        self.assertEqual('Callback not found', str(e.exception))
        self.assertEqual(404, e.exception.status_code)

        mock_delete.return_value = None
        with self.assertRaises(api.ApiError) as e:
            delete_callback(user_id='user2', job_id='job3')

        self.assertEqual('Deletion error', str(e.exception))
        self.assertEqual(401, e.exception.status_code)
        mock_delete_patch.stop()


if __name__ == '__main__':
    unittest.main()
