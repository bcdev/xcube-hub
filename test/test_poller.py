import unittest

from kubernetes.client import V1Pod, V1ObjectMeta, V1PodStatus

from xcube_hub import poller

_CT = 0


class TestPoller(unittest.TestCase):
    def test_poll_pod_phase(self):
        pod = V1Pod(metadata=V1ObjectMeta(name='test'), status=V1PodStatus(phase='Running'))

        def get_pod(prefix: str, namespace=None, label_selector: str = None):
            global _CT
            if _CT == 0:
                _CT += 1
                return None
            elif _CT == 1:
                _CT += 1
                return V1Pod(metadata=V1ObjectMeta(name='test'), status=V1PodStatus(phase='deas'))
            else:
                _CT += 1
                return pod

        poller.poll_pod_phase(get_pod, prefix='test')


if __name__ == '__main__':
    unittest.main()
