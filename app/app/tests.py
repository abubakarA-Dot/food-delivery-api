"""Test Case for Calculating 2 numbers"""
from django.test import SimpleTestCase
from . import calc


class CalculateTests(SimpleTestCase):

    def test_add_numbers(self):
        """Test"""
        res = calc.add_numbers(5, 6)
        self.assertEqual(res, 11)

    def test_substract_numbers(self):
        """Test"""
        res = calc.substract_numbers(25, 36)
        self.assertEqual(res, 11)
