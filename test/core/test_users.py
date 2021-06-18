import unittest

import requests_mock

from xcube_hub import api
from xcube_hub.core import users
from xcube_hub.models.subscription import Subscription
from xcube_hub.models.user import User
from xcube_hub.models.user_user_metadata import UserUserMetadata


class TestUsers(unittest.TestCase):
    @requests_mock.Mocker()
    def test_get_permissions_by_user_id(self, m):
        user = User(email='drwho@mail.org', user_id='drwho', username='drwho', family_name='who', given_name='dr',
                    name='drwho', password='dashc', user_metadata={'client_id': 'snört',
                                                                   'client_secret': 'sdvdsv'},
                    connection='Init',
                    app_metadata={'geodb_role': 'test_role'})

        m.get(f"https://edc.eu.auth0.com/api/v2/users/drwho/permissions", json=user.to_dict())

        res = users.get_permissions_by_user_id('drwho', token='atoken')

        self.assertDictEqual(user.to_dict(), res)

        m.get(f"https://edc.eu.auth0.com/api/v2/users/drwho/permissions", text='No user', status_code=404)

        with self.assertRaises(api.ApiError) as e:
            users.get_permissions_by_user_id('drwho', token='atoken')

        self.assertEqual(404, e.exception.status_code)
        self.assertEqual('User not found.', str(e.exception))

        m.get(f"https://edc.eu.auth0.com/api/v2/users/drwho/permissions", text='Server Error', status_code=500)

        with self.assertRaises(api.ApiError) as e:
            users.get_permissions_by_user_id('drwho', token='atoken')

        self.assertEqual(400, e.exception.status_code)
        self.assertEqual('Server Error', str(e.exception))

    def test_get_request_body_from_user(self):
        user = User(email='drwho@mail.org', user_id='drwho', username='drwho', family_name='who', given_name='dr',
                    name='drwho', password='dashc', user_metadata={'client_id': 'snört',
                                                                   'client_secret': 'sdvdsv'},
                    connection='Init',
                    app_metadata={'geodb_role': 'test_role'})
        res = users.get_request_body_from_user(user)

        for k, v in res.items():
            self.assertIsNotNone(v)

    def test_supplement_user(self):
        user = User(email='drwho@mail.org', user_id='drwho', username='drwho', family_name='who', given_name='dr',
                    name='drwho', password='dashc',
                    connection='Init',
                    app_metadata={'geodb_role': 'test_role'},
                    user_metadata=UserUserMetadata())

        subscription = Subscription(
            subscription_id='ab123',
            email="peter.pettigrew@mail.com",
            plan='free',
            guid='dfvdsv',
            client_id='fdvdv',
            client_secret='sdfvsdvdf',
            units=1000,
            unit='punits',
            first_name='Peter',
            last_name='Pettigrew',
            start_date="2000-01-01",
        )

        res = users.supplement_user(user, subscription)

        self.assertEqual(43, len(res.password))
        self.assertEqual('fdvdv', res.user_metadata.client_id)
        self.assertEqual('sdfvsdvdf', res.user_metadata.client_secret)
        self.assertEqual('a10e508275d003230af34c3b3a5f327e6', res.user_id)


if __name__ == '__main__':
    unittest.main()
