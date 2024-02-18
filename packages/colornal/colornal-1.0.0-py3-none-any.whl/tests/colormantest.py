import unittest
from colornal.box import box


class TestBoxFunction(unittest.TestCase):

    def test_normal_box(self):
        self.assertIsNone(box('A', 'red', 'normal'))

    def test_rounded_box(self):
        self.assertIsNone(box('B', 'blue', 'rounded'))

    def test_double_box(self):
        self.assertIsNone(box('C', 'green', 'double'))

    def test_invalid_box_type(self):
        with self.assertRaises(ValueError):
            box('D', 'yellow', 'invalid')


if __name__ == '__main__':
    unittest.main()
