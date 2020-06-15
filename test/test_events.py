import unittest

from xcube_gen import api
from xcube_gen.events import PutEvents, GetEvents, DeleteEvents


class TestEvents(unittest.TestCase):
    def test_put(self):
        def _run_put(**kwargs):
            pass

        PutEvents.finished += _run_put

        with self.assertRaises(api.ApiError) as e:
            PutEvents.finished()

        self.assertEqual("trigger_punit_substract could not be executed. Callback dict is missing", str(e.exception))

    def test_get(self):
        def _run_get(*args, **kwargs):
            raise api.ApiError(500, "Testing CallbackGet")

        GetEvents.finished += _run_get

        with self.assertRaises(api.ApiError) as e:
            GetEvents.finished(user_id='sdfvdfsv')

        self.assertEqual("Testing CallbackGet", str(e.exception))

    def test_delete(self):
        def _run_delete(*args, **kwargs):
            raise api.ApiError(500, "Testing CallbackDelete")

        DeleteEvents.finished += _run_delete

        with self.assertRaises(api.ApiError) as e:
            DeleteEvents.finished(user_id='sdfvdfsv')

        self.assertEqual("Testing CallbackDelete", str(e.exception))


if __name__ == '__main__':
    unittest.main()
