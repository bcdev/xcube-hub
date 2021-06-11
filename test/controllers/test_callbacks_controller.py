# coding: utf-8

from __future__ import absolute_import

from unittest.mock import patch

from xcube_hub import api
from xcube_hub.controllers.callbacks import put_callback_by_cubegen_id
from xcube_hub.models.callback import Callback
from test import BaseTestCase


class TestCallbacksController(BaseTestCase):
    """CallbacksController integration test stubs"""

    def test_put_callback_by_job_id(self):
        """Test case for put_callback_by_job_id

        Add a callback for a job
        """
        callback = Callback(state={'error': 'dasds'}, sender='on_end')

        res = put_callback_by_cubegen_id(body=callback.to_dict(), cubegen_id='test_id', token_info={
            'access_token': 'dfevgdf',
            'user_id': 'helge',
            'email': 'helge@mail.org'
        })

        expected = ({'progress': [{'sender': 'on_end', 'state': {'error': 'dasds'}}]}, 200)
        self.assertEqual(expected, res)

        # Test whether the controller returns an error when the service raises an exception
        def side_effect(user_id, email, cubegen_id, value):
            raise api.ApiError(400, 'test')

        with patch('xcube_hub.core.callbacks.put_callback') as p:
            p.side_effect = side_effect

            res = put_callback_by_cubegen_id(body=callback.to_dict(), cubegen_id='test_id', token_info={
                'access_token': 'dfevgdf',
                'user_id': 'helge',
                'email': 'helge@mail.org'
            })

            self.assertEqual(400, res[1])
            self.assertEqual('test', res[0]['message'])
            self.assertGreater(len(res[0]['traceback']), 0)


if __name__ == '__main__':
    import unittest

    unittest.main()
