import os
import unittest

from xcube_hub import api
from xcube_hub.util import maybe_raise_for_invalid_username, load_env_by_regex, maybe_raise_for_env


class MyTestCase(unittest.TestCase):
    def test_validate_username(self):
        # Email addresses contain @s
        with self.assertRaises(api.ApiError) as e:
            maybe_raise_for_invalid_username('helge@mäil')

        self.assertEqual("Invalid user name.", str(e.exception))

        # Name too long > 63
        with self.assertRaises(api.ApiError) as e:
            maybe_raise_for_invalid_username('vsdfölvjisdöfvijdsfövlijsdölvjsdfövjsdölvjisdfölvjsdflövjisdflövjisdflövjisdfölvji'
                                       'sdflövjisdflövjisdflövijdfsöl')

        self.assertEqual("Invalid user name.", str(e.exception))

        # Username contains _
        res = maybe_raise_for_invalid_username('user_name')

        self.assertEqual("user-name", res)

    def test_load_env_by_regex(self):
        os.environ["DEBUSSY_LA_MERE"] = "1"
        os.environ["DEBUSSY_CLAIRE_DE_LUNE"] = "2"
        os.environ["DEBUSSY_LA_FILLE_AUX_CHEVEUX_DE_LIN"] = "3"
        os.environ["NOTDEBUSSY_GYMNOPEDIE"] = "4"

        res = load_env_by_regex(r'^DEBUSSY_')
        self.assertEqual(3, len(res))

        res = load_env_by_regex(r'^DEBUSSIE_')
        self.assertEqual(0, len(res))

        # This should return all envs which is DEBUSSY + NOTDEBUSSY + all the rest; hence, must be greater 3
        res = load_env_by_regex()
        self.assertLess(3, len(res))

    def test_maybe_raise_for_env(self):
        # Test "all goes right"
        os.environ['TT'] = "1234"

        val = maybe_raise_for_env('TT')
        self.assertEqual("1234", val)

        # Test type conversion
        val = maybe_raise_for_env('TT', typ=int)
        self.assertEqual(1234, val)
        self.assertIsInstance(val, int)

        # Test type conversion goes wrong
        os.environ['TT'] = "1234dd"
        with self.assertRaises(api.ApiError) as e:
            val = maybe_raise_for_env('TT', typ=int)

        self.assertEqual("invalid literal for int() with base 10: '1234dd'", str(e.exception))

        # Test env var does not exist
        with self.assertRaises(api.ApiError) as e:
            val = maybe_raise_for_env('TT1')

        self.assertEqual("Environment Variable TT1 does not exist.", str(e.exception))

        # Test env var does not exist but returns default value
        val = maybe_raise_for_env('TT1', typ=int, default=0)
        self.assertEqual(0, val)
        self.assertIsInstance(val, int)


if __name__ == '__main__':
    unittest.main()
