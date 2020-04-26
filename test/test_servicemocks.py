import unittest

import flask
from xcube_gen.servicemocks import extend_app
from xcube_gen.servicemocks import new_job
from xcube_gen.servicemocks import get_job
from xcube_gen.servicemocks import get_jobs
from xcube_gen.servicemocks import delete_job
from xcube_gen.servicemocks import delete_jobs
from xcube_gen.servicemocks import JOB_ID_KEY
import time


class ServiceMocksTest(unittest.TestCase):

    # noinspection PyMethodMayBeStatic
    def test_extend_app(self):
        # Just a smoke test
        app = flask.Flask(__name__)
        extend_app(app, '')

    def test_jobs(self):
        user_id = 'bibo'
        job1 = new_job(user_id, dict(duration=0.1))
        self.assertIsNotNone(job1)
        job2 = new_job(user_id, dict(duration=0.1))
        self.assertIsNotNone(job2)
        job3 = new_job(user_id, dict(duration=0.1))
        self.assertIsNotNone(job3)

        time.sleep(0.5)

        job1_id = job1[JOB_ID_KEY]
        job2_id = job2[JOB_ID_KEY]
        job3_id = job3[JOB_ID_KEY]

        job = get_job(user_id, job1_id)
        self.assertIs(job, job1)
        self.assertIn(JOB_ID_KEY, job)
        self.assertIn('status', job)
        self.assertIn('start_time', job['status'])
        self.assertIsNotNone(job['status']['start_time'])

        job = get_job(user_id, job2_id)
        self.assertIs(job, job2)
        self.assertIn(JOB_ID_KEY, job)
        self.assertIn('status', job)
        self.assertIn('start_time', job['status'])
        self.assertIsNotNone(job['status']['start_time'])

        job = get_job(user_id, job3_id)
        self.assertIs(job, job3)
        self.assertIn(JOB_ID_KEY, job)
        self.assertIn('status', job)
        self.assertIn('start_time', job['status'])
        self.assertIsNotNone(job['status']['start_time'])

        self.assertEqual({job1_id, job2_id, job3_id}, set(job[JOB_ID_KEY] for job in get_jobs(user_id)))

        delete_job(user_id, job2_id)
        self.assertEqual({job1_id, job3_id}, set(job[JOB_ID_KEY] for job in get_jobs(user_id)))

        delete_jobs(user_id)
        self.assertEqual([], get_jobs(user_id))
