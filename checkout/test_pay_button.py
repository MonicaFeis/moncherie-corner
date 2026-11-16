"""Tests: the Pay button shows a "please wait" state while going to Stripe (US-10)."""
from django.urls import reverse

from .tests import CheckoutTestCase


class PayButtonTests(CheckoutTestCase):
    def test_pay_button_can_show_a_loading_message(self):
        self.add_to_cart(self.stickers)
        response = self.client.get(reverse("checkout:checkout"))
        self.assertContains(response, 'id="checkout-form"')
        self.assertContains(response, 'id="pay-button"')
        self.assertContains(response, "Taking you to payment")

    def test_checkout_page_loads_the_checkout_script(self):
        self.add_to_cart(self.stickers)
        response = self.client.get(reverse("checkout:checkout"))
        self.assertContains(response, "js/checkout.js")
