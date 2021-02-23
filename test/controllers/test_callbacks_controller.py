# coding: utf-8

from __future__ import absolute_import

from dotenv import load_dotenv

from test.controllers.utils import create_test_token
from xcube_hub.models.callback import Callback
from test import BaseTestCase


class TestCallbacksController(BaseTestCase):
    """CallbacksController integration test stubs"""

    def setUp(self) -> None:
        self._claims, self._token = create_test_token(['manage:cubegens'])
        load_dotenv()

    def test_put_callback_by_job_id(self):
        """Test case for put_callback_by_job_id

        Add a callback for a job
        """
        callback = Callback(state={'error': 'dasds'}, sender='on_end')
        job_id = 'job_id_example'
        response = self.client.open(
            f'/api/v2/cubegens/{job_id}/callbacks',
            method='PUT',
            headers={'Authorization': f'Bearer {self._token}'},
            json=callback.to_dict(),
            content_type='application/json')

        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest

    unittest.main()
