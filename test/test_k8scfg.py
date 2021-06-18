import os
import unittest
from unittest.mock import patch

from kubernetes import config

from xcube_hub.k8scfg import K8sCfg


class TestK8sCfg(unittest.TestCase):
    @patch.object(config, 'load_incluster_config')
    def test_load_config_once(self, incluster_cfg_p):
        K8sCfg.load_config_once()

        self.assertTrue(K8sCfg._config_loaded)
        incluster_cfg_p.assert_called_once()

    @patch.object(config, 'load_incluster_config')
    @patch.object(config, 'load_kube_config')
    def test_load_config(self, cfg_p, incluster_cfg_p):
        os.environ['XCUBE_HUB_RUN_LOCAL'] = "1"
        K8sCfg._load_config()
        cfg_p.assert_called_once()

        os.environ['XCUBE_HUB_RUN_LOCAL'] = "0"
        K8sCfg._load_config()
        incluster_cfg_p.assert_called_once()


if __name__ == '__main__':
    unittest.main()
