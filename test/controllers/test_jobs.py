import os
import unittest

from test.config import SH_CFG
from test.setup_utils import setup_auth, set_env
from xcube_hub.service import new_app
import subprocess


@unittest.skipIf(os.environ.get("UNITTEST_WITH_K8S", False) == 'true', "K8s test supressed.")
class TestJobs(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RUN_LOCAL"] = '1'
        os.environ["XCUBE_GEN_API_CALLBACK_URL"] = 'http://test/'
        self._access_token = setup_auth()
        self._app = new_app()
        self._client = self._app.test_client()
        self._client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer ' + self._access_token['access_token']
        subprocess.call(["kubectl", "create", "namespace", "daffy-duck"])

    def tearDown(self) -> None:
        subprocess.call(["kubectl", "delete", "namespace", "daffy-duck"])

    def test_create(self):
        res = self._client.put('/jobs/daffy-duck', json=SH_CFG)
        self.assertEqual("200 OK", res.status)

    def test_create_without_callback_url(self):
        del os.environ["XCUBE_GEN_API_CALLBACK_URL"]
        res = self._client.put('/jobs/daffy-duck', json=SH_CFG)

        response = res.json

        self.assertEqual(400, res.status_code)
        self.assertEqual('XCUBE_GEN_API_CALLBACK_URL must be given', response['message'])

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
