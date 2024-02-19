# test_calculator.py

import unittest
from calc.calculator import Calculator


class TestCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = Calculator()

    def test_add(self):
        result = self.calculator.add(3, 5)
        self.assertEqual(result, 8)

    def test_subtract(self):
        result = self.calculator.subtract(7, 4)
        self.assertEqual(result, 3)

    def test_multiply(self):
        result = self.calculator.multiply(2, 6)
        self.assertEqual(result, 12)



if __name__ == '__main__':
    unittest.main()
