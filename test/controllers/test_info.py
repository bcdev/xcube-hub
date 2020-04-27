import unittest

from xcube_gen.controllers import info


class InfoTest(unittest.TestCase):

    def test_service_info(self):
        service_info = info.service_info()
        self.assertIsInstance(service_info, dict)
        self.assertIsNotNone(service_info.get('name'))
        self.assertIsNotNone(service_info.get('description'))
        self.assertIsNotNone(service_info.get('version'))
        self.assertIsNotNone(service_info.get('serverStartTime'))
        self.assertIsNotNone(service_info.get('serverCurrentTime'))
        self.assertIsNotNone(service_info.get('serverPID'))
