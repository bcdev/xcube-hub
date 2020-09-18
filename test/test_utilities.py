import unittest

from xcube_gen.utilities import raise_for_invalid_username


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


if __name__ == '__main__':
    unittest.main()
