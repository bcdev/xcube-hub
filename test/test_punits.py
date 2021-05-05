import unittest

import boto3
from moto import mock_s3

from xcube_hub.core.punits import add_punits, get_user_data, subtract_punits, override_punits
from xcube_hub.database import DEFAULT_DB_BUCKET_NAME


class TestPunits(unittest.TestCase):
    @mock_s3
    def test_add_punits(self):
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=DEFAULT_DB_BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
        punits_request_1 = dict(punits=dict(total_count=50000,
                                            user_name='heinrich@gmail.com',
                                            price_amount=200,
                                            price_currency='€'))
        add_punits('heinrich@gmail.com', punits_request_1)

        user_data = get_user_data('heinrich@gmail.com', dataset_name='punits')
        self.assertEqual(50000, user_data['count'])

        subtract_punits('heinrich@gmail.com', punits_request_1)
        user_data = get_user_data('heinrich@gmail.com', dataset_name='punits')
        self.assertEqual(0, user_data['count'])

        add_punits('heinrich@gmail.com', punits_request_1)
        add_punits('heinrich@gmail.com', punits_request_1)
        user_data = get_user_data('heinrich@gmail.com', dataset_name='punits')
        self.assertEqual(100000, user_data['count'])

        override_punits('heinrich@gmail.com', punits_request_1)
        user_data = get_user_data('heinrich@gmail.com', dataset_name='punits')
        self.assertEqual(50000, user_data['count'])


if __name__ == '__main__':
    unittest.main()
