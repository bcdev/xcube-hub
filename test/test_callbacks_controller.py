# coding: utf-8

from __future__ import absolute_import

from flask import json
from xcube_hub.models.callback import Callback  # noqa: E501
from test import BaseTestCase


class TestCallbacksController(BaseTestCase):
    """CallbacksController integration test stubs"""

    def test_delete_callbacks_by_job_id(self):
        """Test case for delete_callbacks_by_job_id

        Clear callbacks for a job
        """
        response = self.client.open(
            '/api/v2/jobs/{job_id}/callbacks'.format(job_id='job_id_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_callbacks_by_job_id(self):
        """Test case for get_callbacks_by_job_id

        Get list of callbacks for a job
        """
        response = self.client.open(
            '/api/v2/jobs/{job_id}/callbacks'.format(job_id='job_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_put_callback_by_job_id(self):
        """Test case for put_callback_by_job_id

        Add a callback for a job
        """
        body = [Callback()]
        response = self.client.open(
            '/api/v2/jobs/{job_id}/callbacks'.format(job_id='job_id_example'),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
