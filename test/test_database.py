import unittest

import boto3
import moto

from xcube_hub.database import DEFAULT_DB_BUCKET_NAME
from xcube_hub.database import Database


class DatabaseTest(unittest.TestCase):
    def test_instance(self):
        database = Database.instance()
        self.assertIsNotNone(database)
        # self.assertEqual('dev', database.profile_name)
        self.assertEqual(DEFAULT_DB_BUCKET_NAME, database.bucket_name)

    def test_user_data_crud(self):
        with moto.mock_s3():
            s3 = boto3.client('s3')
            s3.create_bucket(Bucket=DEFAULT_DB_BUCKET_NAME,
                             CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})

            database = Database()

            dataset_name = 'profile'

            # Assert get_user_data() returns  None, if user does not exist
            actual_user_data = database.get_user_data('sieglinde', dataset_name)
            self.assertEqual(None, actual_user_data)

            # Assert put_user_data() works for arbitrary dicts
            expected_user_data = dict(xcpu_total=37864, xcpu_used=7543)
            database.put_user_data('heinrich', dataset_name, expected_user_data)
            # Assert get_user_data() returns what has been put
            actual_user_data = database.get_user_data('heinrich', dataset_name)
            self.assertEqual(expected_user_data, actual_user_data)

            # Assert put_user_data() overwrites previous value
            expected_user_data = dict(xcpu_total=37864, xcpu_used=9387)
            database.put_user_data('heinrich', dataset_name, expected_user_data)
            # Assert get_user_data() returns what has been put
            actual_user_data = database.get_user_data('heinrich', dataset_name)
            self.assertEqual(expected_user_data, actual_user_data)

            # Assert delete_user_data() can delete existing user
            database.delete_user_data('heinrich', dataset_name)
            # Assert get_user_data() returns  None, if user no longer exists
            actual_user_data = database.get_user_data('heinrich', dataset_name)
            self.assertEqual(None, actual_user_data)

            # Assert delete_user_data() does not fail on non-existing users
            database.delete_user_data('sieglinde', dataset_name)
