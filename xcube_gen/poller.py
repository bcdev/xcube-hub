import polling2

from xcube_gen.controllers import jobs, users
from xcube_gen.xg_types import JsonObject


def poll_job_status(user_id: str, job_id: str, punits_request: JsonObject):
    def _is_finished_status(job_status: dict):
        """Check that the response returned 'success'"""
        print(job_status)
        if job_status['succeeded']:
            users.subtract_processing_units(user_id=user_id, punits_request=punits_request)
            return True
        if job_status['failed']:
            return True
        return False

    def _poll():
        return jobs.status(user_id=user_id, job_id=job_id)

    polling2.poll(
        _poll,
        check_success=_is_finished_status,
        step=10,
        timeout=60*60*24
    )
