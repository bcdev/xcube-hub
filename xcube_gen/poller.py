from typing import Any

import polling2
from kubernetes.client import V1Deployment, V1DeploymentList

from xcube_gen.controllers.users import subtract_processing_units
from xcube_gen.controllers.sizeandcost import get_size_and_cost
from xcube_gen.typedefs import JsonObject


def poll_k8s(poller: Any, check_success: Any, step: int = 1, timeout: int = 3600, **kwargs):
    def _poll():
        return poller(**kwargs)

    polling2.poll(
        _poll,
        check_success=check_success,
        step=step,
        timeout=timeout
    )


def poll_job_status(poller: Any, user_id: str, job_id: str, processing_request: JsonObject):
    def _is_finished_status(job_status: dict):
        """Check that the response returned 'success'"""
        if job_status['succeeded']:
            punits_request = get_size_and_cost(processing_request)
            subtract_processing_units(user_id=user_id, punits_request=punits_request)
            return True
        if job_status['failed']:
            return True
        return False

    poll_k8s(poller=poller, check_success=_is_finished_status, user_id=user_id)


def poll_viewer_status(poller: Any, status='ready', **kwargs):
    def _is_ready_status(deployment: V1Deployment):
        """Check that the response returned 'success'"""
        for st in deployment.status.conditions:
            if st.type == 'Available':
                return True

        return False

    def _is_empty(deployments: V1DeploymentList):
        """Check that the response returned 'success'"""
        return len(deployments.items) == 0

    poll_k8s(poller=poller, check_success=_is_ready_status if status == 'ready' else _is_empty, **kwargs)
