"""Tests: the shopping bag is called "bag" everywhere, also in the web address and page title."""
from django.test import TestCase
from django.urls import reverse


class BagAddressTests(TestCase):
    def test_bag_address_is_bag(self):
        self.assertEqual(reverse("cart:detail"), "/bag/")

    def test_bag_page_title_says_your_bag(self):
        response = self.client.get(reverse("cart:detail"))
        self.assertContains(response, "<title>Your bag | moncherie corner</title>", html=False)
