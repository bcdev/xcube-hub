import unittest

from dotenv import load_dotenv

from xcube_hub import api
from xcube_hub.cfg import Cfg


class TestCfg(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv(dotenv_path='test/.env')

    def test_get_datastore(self):
        Cfg.load_config()
        ds = Cfg.get_datastore('sentinelhub_codede')

        self.assertEqual('sentinelhub', ds['store_id'])

        with self.assertRaises(api.ApiError) as e:
            Cfg.get_datastore('unknown')

        self.assertEqual('Error: Could not load datastore configuration. Datastore unknown not in config.',
                         str(e.exception))

        # Validation switched off as teh hub is not serving the data stores anymore
        # Cfg._datapools_cfg = None
        # with self.assertRaises(api.ApiError) as e:
        #     Cfg.load_config('datapools_invalid.yaml')
        #
        # self.assertIn("Could not validate data pools configuration. 'cost_params' is a required property",
        #               str(e.exception))

        Cfg._datapools_cfg = None
        with self.assertRaises(api.ApiError) as e:
            Cfg.load_config('datapools_not_therer.yaml')

        self.assertEqual("Could not find data pools configuration",
                         str(e.exception))

        # os.environ['XCUBE_HUB_CFG_DATAPOOLS_SCHEMA'] = 'unkown.yaml'
        #
        # Cfg._datapools_cfg = None
        # with self.assertRaises(api.ApiError) as e:
        #     Cfg.load_config('datapools.yaml')
        #
        # self.assertEqual("Could not find data pools validation configuration",
        #                  str(e.exception))


if __name__ == '__main__':
    unittest.main()
