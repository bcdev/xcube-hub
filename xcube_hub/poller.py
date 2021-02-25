from typing import Any, Optional

import polling2
from kubernetes.client import V1Deployment, V1DeploymentList, V1Pod, V1Job, V1JobList


def poll_k8s(poller: Any, check_success: Any, step: int = 1, timeout: int = 3600, **kwargs):
    def _poll():
        return poller(**kwargs)

    polling2.poll(
        _poll,
        check_success=check_success,
        step=step,
        timeout=timeout
    )


def poll_deployment_status(poller: Any, status='ready', **kwargs):
    def _is_status(deployment: V1Deployment):
        if not deployment:
            return False
        """Check that the response returned 'success'"""
        for st in deployment.status.conditions:
            if st.type == 'Available':
                return True

        return False

    def _is_empty(deployments: V1DeploymentList):
        if not deployments:
            return False

        """Check that the response returned 'success'"""
        return len(deployments.items) == 0

    poll_k8s(poller=poller, check_success=_is_status if status == 'ready' else _is_empty, **kwargs)


def poll_pod_phase(poller: Any, phase='running', **kwargs):
    def _is_phase(pod: Optional[V1Pod]) -> bool:
        """Check that the response returned 'success'"""

        if pod is None:
            return False
        elif pod.status.phase.lower() == phase:
            return True
        else:
            return False

    poll_k8s(poller=poller, check_success=_is_phase, **kwargs)


# noinspection DuplicatedCode
def poll_job_status(poller: Any, status='ready', **kwargs):
    def _is_status(job: V1Job):
        if not job:
            return False
        """Check that the response returned 'success'"""
        if job.status.conditions is not None:
            for st in job.status.conditions:
                if st.type == 'Complete':
                    return True

        return False

    def _is_empty(jobs: V1JobList):
        if not jobs:
            return False

        """Check that the response returned 'success'"""
        return len(jobs.items) == 0

    poll_k8s(poller=poller, check_success=_is_status if status == 'ready' else _is_empty, **kwargs)
