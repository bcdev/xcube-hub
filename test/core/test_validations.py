import os

from dotenv import load_dotenv

from test import BaseTestCase
from xcube_hub import api
from xcube_hub.core.validations import validate_env, validate_datapools


class TestValidations(BaseTestCase):
    def setUp(self):
        load_dotenv(dotenv_path='test/.env')

    def test_validate_env(self):
        res = validate_env()
        self.assertTrue(res)

        del os.environ['AUTH0_USER_MANAGEMENT_CLIENT_ID']
        with self.assertRaises(api.ApiError) as e:
            validate_env()

        self.assertEqual("Env var AUTH0_USER_MANAGEMENT_CLIENT_ID required.", str(e.exception))

    def test_validate_datapools(self):
        res = validate_datapools()
        self.assertTrue(res)

        os.environ["XCUBE_HUB_CFG_DATAPOOLS"] = "data-pools-invalid.yaml"
        with self.assertRaises(api.ApiError) as e:
            res = validate_datapools()

        self.assertIn("'cost_params' is a required property", str(e.exception))

        os.environ["XCUBE_HUB_CFG_DATAPOOLS"] = "data-pools-not-exist.yaml"
        with self.assertRaises(api.ApiError) as e:
            res = validate_datapools()

        self.assertEqual('Could not find data pools configuration', str(e.exception))

        os.environ["XCUBE_HUB_CFG_DATAPOOLS"] = "data-pools.yaml"
        os.environ["XCUBE_HUB_CFG_DATAPOOLS_SCHEMA"] = "data-pools-schema-not-exist.yaml"
        with self.assertRaises(api.ApiError) as e:
            res = validate_datapools()

        self.assertEqual('Could not find data pools configuration', str(e.exception))

        del os.environ["XCUBE_HUB_CFG_DATAPOOLS"]
        with self.assertRaises(api.ApiError) as e:
            res = validate_datapools()

        self.assertEqual('Environment Variable XCUBE_HUB_CFG_DATAPOOLS does not exist.', str(e.exception))


if __name__ == '__main__':
    import unittest

    unittest.main()
