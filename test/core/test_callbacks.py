import unittest

import boto3
from jose import jwt
from moto import mock_s3

from xcube_hub import api
from xcube_hub.controllers.punits import add_punits, get_user_data
from xcube_hub.core.callbacks import get_callback, put_callback
from xcube_hub.database import DEFAULT_DB_BUCKET_NAME
from xcube_hub.keyvaluedatabase import KeyValueDatabase


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

TOKEN = jwt.encode(TEST_CLAIMS, "ysdfvdfvdsvfdsvfdvs", algorithm="HS256")


class TestCallbacks(unittest.TestCase):
    def setUp(self) -> None:
        self._cache = KeyValueDatabase.instance(provider='inmemory')
        self._cache.set('heinrich__cubegen', {'value_key': 'value'})
        self._cache.set('heinrich__cubegen__cfg', CUBEGEN_TEST)
        self._token = jwt.encode(TEST_CLAIMS, "ysdfvdfvdsvfdsvfdvs", algorithm="HS256")

    def test_get_callback(self):
        res = get_callback('heinrich', 'cubegen')

        self.assertDictEqual({'value_key': 'value'}, res)

        with self.assertRaises(api.ApiError) as e:
            get_callback('heinrich', 'cubegen2')

        self.assertEqual(404, e.exception.status_code)
        self.assertEqual("Could not find any callback entries for that key.", str(e.exception))

    @mock_s3
    def test_put_callback(self):
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=DEFAULT_DB_BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
        punits_request_1 = dict(punits=dict(total_count=50000,
                                            user_name='heinrich@gmail.com',
                                            price_amount=200,
                                            price_currency='€'))
        add_punits('heinrich@gmail.com', punits_request_1)

        cfg = {'state': {'error': 'Error'}, 'sender': 'on_end'}
        put_callback('heinrich', 'cubegen', cfg, token=self._token)
        user_data = get_user_data('heinrich@gmail.com', dataset_name='punits')
        self.assertEqual(50000, user_data['count'])

        cfg = {'state': {}, 'sender': 'on_end'}
        put_callback('heinrich', 'cubegen', cfg, token=self._token)
        user_data = get_user_data('heinrich@gmail.com', dataset_name='punits')
        self.assertEqual(40660, user_data['count'])


if __name__ == '__main__':
    unittest.main()
