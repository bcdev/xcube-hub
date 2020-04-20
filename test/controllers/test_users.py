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
            processing_units = user_data.get('processingUnits')
            self.assertEqual(5000, processing_units.get('count'))
            self.assertIsInstance(processing_units.get('history'), list)
            self.assertEqual(1, len(processing_units.get('history')))

            update_processing_units('heinrich', 'charge', 2000)
            update_processing_units('heinrich', 'consume', 3000)
            user_data = get_user_data('heinrich')
            processing_units = user_data.get('processingUnits')
            self.assertEqual(4000, processing_units.get('count'))
            self.assertIsInstance(processing_units.get('history'), list)
            self.assertEqual(3, len(processing_units.get('history')))
