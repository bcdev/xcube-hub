import os
import unittest
from unittest.mock import patch

from test.config import SH_CFG
from test.setup_utils import set_env
from xcube_hub import api
from xcube_hub.controllers import jobs
from xcube_hub.service import new_app
import subprocess


# @unittest.skipIf(os.environ.get("UNITTEST_WITH_K8S", False) == 'true', "K8s test supressed.")
@patch("xcube_hub.auth0.Auth0.get_token_auth_header", return_value="sdfvfsdvdfsv")
class TestJobs(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["XCUBE_GEN_API_RUN_LOCAL"] = '1'
        os.environ["XCUBE_GEN_API_CALLBACK_URL"] = 'http://test/'
        self._app = new_app()
        # self._client = self._app.test_client()
        # self._token = setup_auth()
        # self._client.head('Authorization: Bearer ' + self._token['access token'])
        subprocess.call(["kubectl", "create", "namespace", "daffy-duck"])

    def tearDown(self) -> None:
        subprocess.call(["kubectl", "delete", "namespace", "daffy-duck"])

    def test_create(self, m_header):
        res = jobs.create('daffy-duck', SH_CFG)
        self.assertEqual("ok", res['status'])

    def test_create_without_callback_url(self, m_header):
        del os.environ["XCUBE_GEN_API_CALLBACK_URL"]
        with self.assertRaises(api.ApiError) as e:
            jobs.create('daffy-duck', SH_CFG)

        self.assertEqual('XCUBE_GEN_API_CALLBACK_URL must be given', str(e.exception))

    def test_delete(self, m_header):
        set_env()
        with self.assertRaises(api.ApiError) as e:
            jobs.delete_one('daffy-duck', 'a-test')

        self.assertEqual(404, e.exception.status_code)

    def test_get(self, m_header):
        set_env()
        with self.assertRaises(api.ApiError) as e:
            jobs.get('daffy-duck', 'a-test')

        self.assertEqual(404, e.exception.status_code)

    def test_delete_all(self, m_header):
        set_env()
        res = jobs.delete_all('daffy-duck')

        self.assertEqual('ok', res['status'])


if __name__ == '__main__':
    unittest.main()
