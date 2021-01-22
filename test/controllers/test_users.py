import hashlib
import unittest

from moto import mock_s3
import boto3

from xcube_hub.controllers.users import get_user_data
from xcube_hub.controllers.users import add_processing_units
from xcube_hub.controllers.users import subtract_processing_units
from xcube_hub.database import DEFAULT_DB_BUCKET_NAME


class UsersTest(unittest.TestCase):
    # noinspection InsecureHash
    @mock_s3
    def test_update_processing_units(self):
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=DEFAULT_DB_BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})

        user_name = 'heinrich'
        user_id = hashlib.md5(user_name.encode('utf-8')).hexdigest()

        punits_request_1 = dict(punits=dict(total_count=5000,
                                user_name=user_name,
                                price_amount=200,
                                price_currency='€'))
        punits_request_2 = dict(punits=dict(total_count=10000,
                                user_name=user_name,
                                price_amount=350,
                                price_currency='€'))
        punits_request_3 = dict(punits=dict(total_count=280,
                                user_name=user_name))

        add_processing_units(user_id, punits_request_1)

        add_processing_units(user_id, punits_request_2)

        subtract_processing_units(user_id, punits_request_3)

        punits_data = get_user_data(user_id, 'punits')
        self.assertIsNotNone(punits_data)
        self.assertIn('count', punits_data)
        self.assertIn('history', punits_data)
        actual_count = punits_data.get('count')
        actual_history = punits_data.get('history')
        self.assertEqual(5000 + 10000 - 280, actual_count)
        self.assertIsInstance(actual_history, list)
        self.assertEqual(3, len(actual_history))
        self.assertEqual(['sub', punits_request_3], actual_history[0][1:])
        self.assertEqual(['add', punits_request_2], actual_history[1][1:])
        self.assertEqual(['add', punits_request_1], actual_history[2][1:])
