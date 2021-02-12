# coding: utf-8

from __future__ import absolute_import

from flask import json
from xcube_hub.models.cost_config import CostConfig  # noqa: E501
from xcube_hub.models.job_config import JobConfig  # noqa: E501
from xcube_hub.test import BaseTestCase


class TestJobsController(BaseTestCase):
    """JobsController integration test stubs"""

    def test_create_job(self):
        """Test case for create_job

        Create a job
        """
        body = JobConfig()
        response = self.client.open(
            '/api/v1/jobs',
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_job(self):
        """Test case for delete_job

        Delete a job
        """
        response = self.client.open(
            '/api/v1/jobs/{job_id}'.format(job_id='job_id_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_jobs(self):
        """Test case for delete_jobs

        Delete all jobs
        """
        response = self.client.open(
            '/api/v1/jobs',
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_costs(self):
        """Test case for get_costs

        Receive cost information for runnning a job
        """
        body = CostConfig()
        response = self.client.open(
            '/api/v1/jobs/costs',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_job(self):
        """Test case for get_job

        List specific job
        """
        response = self.client.open(
            '/api/v1/jobs/{job_id}'.format(job_id='job_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_jobs(self):
        """Test case for get_jobs

        List jobs
        """
        response = self.client.open(
            '/api/v1/jobs',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
