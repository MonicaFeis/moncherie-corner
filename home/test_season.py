"""Tests: success messages show iced bubble milk tea in summer, hot milk tea the rest of the year."""
from django.test import SimpleTestCase

from home.context_processors import drink_for_month


class SeasonDrinkTests(SimpleTestCase):
    def test_summer_months_get_bubble_milk_tea(self):
        for month in [6, 7, 8, 9, 10]:
            self.assertEqual(drink_for_month(month), "🧋")

    def test_other_months_get_hot_milk_tea(self):
        for month in [1, 2, 3, 4, 5, 11, 12]:
            self.assertEqual(drink_for_month(month), "☕")
