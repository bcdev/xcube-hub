import unittest

from xcube_hub.api import get_json_request_value, ApiError


class ApiErrorTest(unittest.TestCase):
    def test_it(self):
        error = ApiError(403, 'hands off')
        self.assertEqual(403, error.status_code)
        self.assertEqual('hands off', f'{error}')
        self.assertEqual((dict(message='hands off', traceback='NoneType: None\n'), 403),
                         error.response)


class GetJsonResponseTest(unittest.TestCase):
    def test_get_json_request_value_to_succeed(self):
        self.assertEqual('Bibo', get_json_request_value(dict(name='Bibo'), 'name'))
        self.assertEqual(True, get_json_request_value(dict(ok=True), 'ok'))
        self.assertEqual('Bibo', get_json_request_value(dict(name='Bibo'), 'name', value_type=str))
        self.assertEqual(None, get_json_request_value(dict(), 'name', default_value=None))
        self.assertEqual('Bert', get_json_request_value(dict(), 'name', default_value='Bert'))

    def test_get_json_request_value_to_fail_expectedly(self):
        with self.assertRaises(ApiError) as cm:
            # noinspection PyTypeChecker
            get_json_request_value('test', 'name')
        self.assertEqual('request must be a JSON object', f'{cm.exception}')

        with self.assertRaises(ApiError) as cm:
            get_json_request_value(dict(), 'name')
        self.assertEqual('missing request key "name"', f'{cm.exception}')

        with self.assertRaises(ApiError) as cm:
            get_json_request_value(dict(name=False), 'name', value_type=str)
        self.assertEqual('value for request key "name" is of wrong type: '
                         'expected type str, got type bool',
                         f'{cm.exception}')

        with self.assertRaises(ApiError) as cm:
            get_json_request_value(dict(ratio='zero'), 'ratio', value_type=(float, int))
        self.assertEqual('value for request key "ratio" is of wrong type: '
                         'expected type float or int, got type str',
                         f'{cm.exception}')

        with self.assertRaises(ApiError) as cm:
            get_json_request_value(dict(tile_size=[5000]), 'tile_size',
                                   value_type=list, item_count=2, item_type=int)
        self.assertEqual('value for request key "tile_size" must be a list of length 2, got length 1',
                         f'{cm.exception}')

        with self.assertRaises(ApiError) as cm:
            get_json_request_value(dict(tile_size=[5000, None]), 'tile_size',
                                   value_type=list, item_count=2, item_type=int)
        self.assertEqual('value for request key "tile_size" has an item of wrong type: '
                         'expected type int, got type NoneType',
                         f'{cm.exception}')