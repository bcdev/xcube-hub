# coding: utf-8

from __future__ import absolute_import

from flask import json

from test.controllers.utils import create_test_token
from xcube_hub.models.callback import Callback  # noqa: E501
from test import BaseTestCase


class TestCallbacksController(BaseTestCase):
    """CallbacksController integration test stubs"""

    def setUp(self) -> None:
        self._claims, self._token = create_test_token(['manage:callbacks'])

    def test_put_callback_by_job_id(self):
        """Test case for put_callback_by_job_id

        Add a callback for a job
        """
        body = [Callback(state={'error': 'dasds'}, sender='on_end', message="sdfv", values={"dfv": 'ff'}, total_worked=90.,
                         worked=80.), ]
        response = self.client.open(
            '/api/v2/cubegens/{job_id}/callbacks'.format(job_id='job_id_example'),
            method='PUT',
            headers={'Authorization': f'Bearer {self._token}'},
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest

    unittest.main()
