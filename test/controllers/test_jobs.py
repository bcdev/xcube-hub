import os
import unittest
from unittest.mock import patch, Mock

from test.config import SH_CFG
from test.setup_utils import set_env
import xcube_hub.auth0
from xcube_hub.controllers import jobs
from xcube_hub.service import new_app
import subprocess


# @unittest.skipIf(os.environ.get("UNITTEST_WITH_K8S", False) == 'true', "K8s test supressed.")
class TestJobs(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["XCUBE_GEN_API_RUN_LOCAL"] = '1'
        os.environ["XCUBE_GEN_API_CALLBACK_URL"] = 'http://test/'
        self._app = new_app()
        subprocess.call(["kubectl", "create", "namespace", "daffy-duck"])

    def tearDown(self) -> None:
        subprocess.call(["kubectl", "delete", "namespace", "daffy-duck"])

    def test_create(self):
        mock_token_auth_patch = patch('xcube_hub.auth0.get_token_auth_header')
        mock_tocken_auth = mock_token_auth_patch.start()
        mock_tocken_auth.return_value = "akuicvgkasduczgdkauscgkauscdz"

        res = jobs.create('daffy-duck', SH_CFG)
        # res = self._client.put('/jobs/daffy-duck', json=SH_CFG)
        self.assertEqual("200 OK", res.status)

        # mock_token_auth_patch.stop()

    def test_create_without_callback_url(self):
        del os.environ["XCUBE_GEN_API_CALLBACK_URL"]
        res = jobs.create('daffy-duck', SH_CFG)
        self.assertEqual('XCUBE_GEN_API_CALLBACK_URL must be given', 'message')

    def test_delete(self):
        set_env()
        res = jobs.delete_one('daffy-duck', 'a-test')
        self.assertEqual('404 NOT FOUND', res.status)

    def test_get(self):
        set_env()
        res = jobs.get('daffy-duck', 'a-test')
        self.assertEqual('404 NOT FOUND', res.status)

    def test_list(self):
        set_env()
        res = jobs.get('daffy-duck', 'a-test')
        self.assertEqual('200 OK', res.status)

    def test_delete_all(self):
        set_env()
        res = jobs.delete_all('daffy-duck')
        self.assertEqual('200 OK', res.status)


if __name__ == '__main__':
    unittest.main()
