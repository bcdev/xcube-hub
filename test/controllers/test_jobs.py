import unittest

from test.setup_auth import setup_auth
from xcube_gen.service import new_app


class TestJobs(unittest.TestCase):
    def setUp(self) -> None:
        self._access_token = setup_auth()
        self._app = new_app()
        self._client = self._app.test_client()

    def test_list(self):
        res = self._client.get('/jobs/daffy_duck')
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
