import unittest

from xcube_gen.controllers.users import update_processing_units
from xcube_gen.controllers.users import get_user_data

import moto
import boto3

from xcube_gen.database import DEFAULT_DB_BUCKET_NAME


class UsersTest(unittest.TestCase):
    def test_update_processing_units(self):
        with moto.mock_s3():
            s3 = boto3.client('s3')
            s3.create_bucket(Bucket=DEFAULT_DB_BUCKET_NAME)

            update_processing_units('heinrich', 'charge', 5000)
            user_data = get_user_data('heinrich')
            self.assertEqual(5000, user_data.get('processing_units_total'))
            self.assertIsInstance(user_data.get('processing_units_history'), list)
            self.assertEqual(1, len(user_data.get('processing_units_history')))

            update_processing_units('heinrich', 'charge', 2000)
            update_processing_units('heinrich', 'consume', 3000)
            user_data = get_user_data('heinrich')
            self.assertEqual(4000, user_data.get('processing_units_total'))
            self.assertIsInstance(user_data.get('processing_units_history'), list)
            self.assertEqual(3, len(user_data.get('processing_units_history')))
