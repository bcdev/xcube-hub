import unittest
from unittest.mock import patch

import boto3
from dotenv import load_dotenv
from jose import jwt
from moto import mock_aws

from xcube_hub import api
from xcube_hub.cfg import Cfg
from xcube_hub.core.punits import add_punits, get_user_data
from xcube_hub.core.callbacks import put_callback, get_callback
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
        "size_estimation": {
            "image_size": [34, 54],
            "tile_size": [34, 54],
            "num_variables": 3,
            "num_tiles": [1, 1],
            "num_requests": 0,
            "num_bytes": 0
        },
        "cost_estimation": {
            'required': 3782,
            'available': 234979,
            'limit': 10000
        },
        "dataset_descriptor": {
            "type_specifier": "dataset",
            "data_id": "CHL",
            "crs": "WGS84",
            "bbox": [12.2, 52.1, 13.9, 54.8],
            "time_range": ["2018-01-01", "2010-01-06"],
            "time_period": "4D",
            "data_vars": {
                "B01": {
                    "name": "B01",
                    "dtype": "float32",
                    "dims": ["time", "lat", "lon"],
                },
                "B02": {
                    "name": "B02",
                    "dtype": "float32",
                    "dims": [
                        "time",
                        "lat",
                        "lon"
                    ],
                },
                "B03": {
                    "name": "B03",
                    "dtype": "float32",
                    "dims": ["time", "lat", "lon"],
                }
            },
            "spatial_res": 0.05,
            "dims": {"time": 10, "lat": 54, "lon": 34}
        }
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
        self._cache.set('heinrich2__cubegen', {'value_key': 'value', 'progress': [100, ]})
        self._token = jwt.encode(TEST_CLAIMS, "ysdfvdfvdsvfdsvfdvs", algorithm="HS256")
        load_dotenv(dotenv_path='test/.env')
        Cfg.load_config()

    def test_get_callback(self):
        res = get_callback('heinrich', 'cubegen')

        self.assertDictEqual({'value_key': 'value'}, res)

        res = get_callback('heinrich', 'cubegen2')

        self.assertDictEqual({}, res)

        res = get_callback('heinrich2', 'cubegen')

        self.assertEqual([100, ], res)

        cache = KeyValueDatabase.instance()

        with patch.object(cache, 'get') as p:
            p.side_effect = TimeoutError()

            with self.assertRaises(api.ApiError) as e:
                get_callback('heinrich2', 'cubegen')

            self.assertEqual("Cache timout", str(e.exception))

    @mock_aws
    def test_put_callback(self):
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=DEFAULT_DB_BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
        punits_request_1 = dict(punits=dict(total_count=50000,
                                            user_name='heinrich@gmail.com',
                                            price_amount=200,
                                            price_currency='€'))
        add_punits('heinrich@gmail.com', punits_request_1)

        cfg = {'sender': 'on_begin'}
        with self.assertRaises(api.ApiError) as e:
            put_callback(user_id='heinrich', cubegen_id='cubegen', email='heinrich@gmail.com', value=cfg)

        self.assertEqual(401, e.exception.status_code)
        self.assertEqual('Callbacks need a "state"', str(e.exception))
        user_data = get_user_data('heinrich@gmail.com', dataset_name='punits')
        self.assertEqual(50000, user_data['count'])

        cfg = {'state': {}, 'sender': 'on_begin'}
        put_callback(user_id='heinrich', cubegen_id='cubegen', email='heinrich@gmail.com', value=cfg)
        user_data = get_user_data('heinrich@gmail.com', dataset_name='punits')
        self.assertEqual(50000, user_data['count'])

        cfg = {'state': {'error': 'Error'}, 'sender': 'on_end'}
        put_callback(user_id='heinrich', cubegen_id='cubegen', email='heinrich@gmail.com', value=cfg)
        user_data = get_user_data('heinrich@gmail.com', dataset_name='punits')
        self.assertEqual(50000, user_data['count'])

        cfg = {'state': {}, 'sender': 'on_end'}
        put_callback(user_id='heinrich', cubegen_id='cubegen', email='heinrich@gmail.com', value=cfg)
        user_data = get_user_data('heinrich@gmail.com', dataset_name='punits')
        self.assertEqual(49970, user_data['count'])

        cfg = {'state': {}, 'sender': 'on_end'}
        cubegen_test = CUBEGEN_TEST.copy()
        cubegen_test['input_config'] = cubegen_test['input_configs'][0]
        del cubegen_test['input_configs']
        self._cache.set('heinrich__cubegen__cfg', cubegen_test)

        put_callback(user_id='heinrich', cubegen_id='cubegen', email='heinrich@gmail.com', value=cfg)
        user_data = get_user_data('heinrich@gmail.com', dataset_name='punits')
        # The above minus 30 from the above substraction
        self.assertEqual(49940, user_data['count'])

        # cfg = {'state': {}, 'sender': 'on_end'}
        # put_callback(user_id='heinrich', cubegen_id='cubegen', email='heinrich@gmail.com', value=cfg)
        # user_data = get_user_data('heinrich@gmail.com', dataset_name='punits')

        cfg = {'state': {}, 'sender': 'on_end'}
        cubegen_test = CUBEGEN_TEST.copy()
        del cubegen_test['input_configs']
        self._cache.set('heinrich__cubegen__cfg', cubegen_test)
        with self.assertRaises(api.ApiError) as e:
            put_callback(user_id='heinrich', cubegen_id='cubegen', email='heinrich@gmail.com', value=cfg)

        self.assertEqual("Error in callbacks. Invalid input configuration.", str(e.exception))

        cache = KeyValueDatabase.instance()
        with patch.object(cache, 'get') as p:
            p.side_effect = TimeoutError()

            with self.assertRaises(api.ApiError) as e:
                put_callback(user_id='heinrich', cubegen_id='cubegen', email='heinrich@gmail.com', value=cfg)

            self.assertEqual("Cache timeout", str(e.exception))


if __name__ == '__main__':
    unittest.main()
