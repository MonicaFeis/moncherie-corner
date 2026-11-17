"""Tests: the checkout page has a way back to the bag to change the order."""
from django.urls import reverse

from .tests import CheckoutTestCase


class CheckoutBackLinkTests(CheckoutTestCase):
    def test_checkout_has_edit_bag_button(self):
        self.add_to_cart(self.stickers)
        response = self.client.get(reverse("checkout:checkout"))
        self.assertContains(response, "修改購物袋 Edit my bag")
        self.assertContains(response, f'href="{reverse("cart:detail")}"')
