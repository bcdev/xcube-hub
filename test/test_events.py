import unittest

from test.config import SH_CFG
from xcube_gen import api
from xcube_gen.cache import Cache
from xcube_gen.events import PutEvents, GetEvents, DeleteEvents, trigger_punit_substract


class TestEvents(unittest.TestCase):
    def setUp(self) -> None:
        Cache.configure('inmemory')

        self._sh_cfg = SH_CFG

    def test_put(self):
        def _run_put(**kwargs):
            pass

        PutEvents.finished += _run_put

        with self.assertRaises(api.ApiError) as e:
            PutEvents.finished()

        self.assertEqual("System error (trigger_punit_substract): Callback dict is missing.", str(e.exception))

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

    def test_trigger_punit_substract(self):
        job_id = "ksjndlskvjdfskvnj"
        user_id = "ci-unittest-user"

        with self.assertRaises(api.ApiError) as e:
            trigger_punit_substract(job_id=job_id, value={})

        self.assertEqual('System error (trigger_punit_substract): user_id is missing.', str(e.exception))

        with self.assertRaises(api.ApiError) as e:
            trigger_punit_substract(user_id=user_id, value={})

        self.assertEqual('System error (trigger_punit_substract): job_id is missing.', str(e.exception))

        with self.assertRaises(api.ApiError) as e:
            trigger_punit_substract(user_id=user_id, job_id=job_id)

        self.assertEqual('System error (trigger_punit_substract): Callback dict is missing.', str(e.exception))

        value = {
            'status': 'CUBE_GENERATED2'
        }

        with self.assertRaises(api.ApiError) as e:
            trigger_punit_substract(value=value, user_id=user_id, job_id=job_id)

        message = "System error (trigger_punit_substract): Job status has to be CUBE_GENERATED before " \
                  "I can substract punits."

        self.assertEqual(message, str(e.exception))

        value = {
            'status': 'CUBE_GENERATED'
        }

        with self.assertRaises(api.ApiError) as e:
            trigger_punit_substract(value=value, user_id=user_id, job_id='hhh')

        message = "System error (trigger_punit_substract): Could not find job."

        self.assertEqual(message, str(e.exception))

        cache = Cache()
        cache.set(job_id, SH_CFG)

        res = trigger_punit_substract(value=value, user_id=user_id, job_id=job_id)
        self.assertTrue(res)


if __name__ == '__main__':
    unittest.main()
