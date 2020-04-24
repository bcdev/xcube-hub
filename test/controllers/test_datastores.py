import unittest
from xcube_gen.controllers.datastores import get_datastores


class DatastoresTest(unittest.TestCase):
    def test_get_datastores(self):
        # Just a smoke test
        response = get_datastores()
        self.assertIsInstance(response, dict)
