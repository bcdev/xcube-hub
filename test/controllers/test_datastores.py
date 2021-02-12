import unittest
from xcube_hub_old.controllers.datastores import get_datastores


class DatastoresTest(unittest.TestCase):
    def test_get_datastores(self):
        # Just a smoke test
        response = get_datastores()
        self.assertIsInstance(response, dict)
