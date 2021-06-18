import unittest
from unittest.mock import patch

from xcube_hub.core import punits
from xcube_hub.database import Database


class TestPunits(unittest.TestCase):
    def test_get_punits(self):
        with patch.object(Database, 'get_user_data') as p:
            p.return_value = {'count': 1000, 'history': []}
            res = punits.get_punits('drwho')
            self.assertDictEqual({'count': 1000}, res)

            p.return_value = {'count': 1000, 'history': []}
            res = punits.get_punits('drwho', include_history=True)
            self.assertDictEqual({'count': 1000, 'history': []}, res)

    def test_delete_punits(self):
        with patch.object(Database, 'delete_user_data') as p:
            p.return_value = {'count': 1000, 'history': []}
            punits.delete_user_data('drwho')

            p.assert_called_once()


if __name__ == '__main__':
    unittest.main()
