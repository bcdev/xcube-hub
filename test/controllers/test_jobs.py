import os
import unittest
from unittest.mock import patch

from test.config import SH_CFG
from test.setup_utils import set_env
from xcube_hub_old import api
from xcube_hub_old.controllers import jobs
from xcube_hub_old.service import new_app
import subprocess


@patch("xcube_hub.auth0.Auth0.get_token_auth_header", return_value="sdfvfsdvdfsv")
class TestJobs(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["XCUBE_HUB_RUN_LOCAL"] = '1'
        os.environ["XCUBE_GEN_API_CALLBACK_URL"] = 'http://test/'
        self._app = new_app()
        subprocess.call(["kubectl", "create", "namespace", "daffy-duck"])

    def tearDown(self) -> None:
        subprocess.call(["kubectl", "delete", "namespace", "daffy-duck"])

    def test_create(self, m_header):
        res = jobs.create('daffy-duck', SH_CFG)
        self.assertEqual("ok", res['status'])

    def test_create_without_callback_url(self, m_header):
        del os.environ["XCUBE_HUB_CALLBACK_URL"]
        with self.assertRaises(api.ApiError) as e:
            jobs.create('daffy-duck', SH_CFG)

        self.assertEqual('XCUBE_HUB_CALLBACK_URL must be given', str(e.exception))

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
