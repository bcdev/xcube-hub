import os
import unittest

from test.setup_utils import setup_auth, set_env
from xcube_gen.service import new_app
import subprocess


class TestJobs(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RUN_LOCAL"] = '1'
        self._access_token = setup_auth()
        self._app = new_app()
        self._client = self._app.test_client()
        self._client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer ' + self._access_token['access_token']
        subprocess.call(["kubectl", "create", "namespace", "daffy-duck"])

    def tearDown(self) -> None:
        subprocess.call(["kubectl", "delete", "namespace", "daffy-duck"])

    def test_create(self):
        res = self._client.post('/jobs/daffy-duck')
        self.assertEqual('400 BAD REQUEST', res.status)
        self.assertEqual('Could not find any xcube-sh docker image.', res.json['message'])

        os.environ["XCUBE_SH_DOCKER_IMG"] = 'quay.io/bcdev/xcube-sh'
        res = self._client.post('/jobs/daffy-duck')
        self.assertEqual('400 BAD REQUEST', res.status)
        self.assertEqual('SentinelHub credentials invalid. Please contact Brockmann Consult', res.json['message'])

        os.environ["SH_CLIENT_ID"] = 'b3da42b1-eef1-4e8d-bf29-dd391ef04518'
        os.environ["SH_CLIENT_SECRET"] = 'ba%k,jsQn:Y<ph:m,j+C/jiG_k$KFlpZ}yAz*E]{'
        os.environ["SH_INSTANCE_ID"] = 'c5828fc7-aa47-4f1d-b684-ae596521ef25'
        res = self._client.post('/jobs/daffy-duck')
        self.assertEqual('200 OK', res.status)
        self.assertGreater(len(res.json['result']['job']), 0)

    def test_delete(self):
        set_env()
        res = self._client.delete('/jobs/daffy-duck/a-test')
        self.assertEqual('404 NOT FOUND', res.status)

    def test_get(self):
        set_env()
        res = self._client.get('/jobs/daffy-duck/a-test')
        self.assertEqual('404 NOT FOUND', res.status)

    def test_list(self):
        set_env()
        res = self._client.get('/jobs/daffy-duck')
        self.assertEqual('200 OK', res.status)

    def test_delete_all(self):
        set_env()
        res = self._client.delete('/jobs/daffy-duck')
        self.assertEqual('200 OK', res.status)


if __name__ == '__main__':
    unittest.main()
