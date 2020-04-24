import os
import unittest

from test.setup_utils import setup_auth
from xcube_gen.controllers.users import update_processing_units
from xcube_gen.controllers.users import get_user_data

import moto
import boto3

from xcube_gen.database import DEFAULT_DB_BUCKET_NAME
from xcube_gen.service import new_app


class UsersTest(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RUN_LOCAL"] = '1'
        self._access_token = setup_auth()
        self._app = new_app()
        self._client = self._app.test_client()
        self._client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer ' + self._access_token['access_token']

    def test_update_processing_units(self):
        with moto.mock_s3():
            s3 = boto3.client('s3')
            s3.create_bucket(Bucket=DEFAULT_DB_BUCKET_NAME)

            update_processing_units('heinrich', dict(count=5000), factor=1)
            processing_units = get_user_data('heinrich', 'punits')
            self.assertIsNotNone(processing_units)
            self.assertEqual(5000, processing_units.get('count'))
            self.assertIsInstance(processing_units.get('history'), list)
            self.assertEqual(1, len(processing_units.get('history')))

            update_processing_units('heinrich', dict(count=2000), factor=1)
            update_processing_units('heinrich', dict(count=3000), factor=-1)
            processing_units = get_user_data('heinrich', 'punits')
            self.assertIsNotNone(processing_units)
            self.assertEqual(4000, processing_units.get('count'))
            self.assertIsInstance(processing_units.get('history'), list)
            self.assertEqual(3, len(processing_units.get('history')))
