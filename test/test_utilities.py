import os
import unittest
from xcube_hub.utilities import raise_for_invalid_username, load_env_by_regex


class MyTestCase(unittest.TestCase):
    def test_validate_username(self):
        # Email addresses contain @s
        with self.assertRaises(ValueError) as e:
            raise_for_invalid_username('helge@mail')

        self.assertEqual("Invalid user name.", str(e.exception))

        # Name too long > 63
        with self.assertRaises(ValueError) as e:
            raise_for_invalid_username('vsdfölvjisdöfvijdsfövlijsdölvjsdfövjsdölvjisdfölvjsdflövjisdflövjisdflövjisdfölvji'
                              'sdflövjisdflövjisdflövijdfsöl')

        self.assertEqual("Invalid user name.", str(e.exception))

        # Username contains _
        with self.assertRaises(ValueError) as e:
            raise_for_invalid_username('user_name')

        self.assertEqual("Invalid user name.", str(e.exception))

        res = raise_for_invalid_username('that-moron')
        self.assertTrue(res)

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


if __name__ == '__main__':
    unittest.main()
