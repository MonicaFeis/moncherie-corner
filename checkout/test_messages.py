"""Tests: customers are told a portrait is drawn after payment, not downloaded straight away (US-34)."""
from decimal import Decimal

from django.core import mail

from notifications.emails import send_order_confirmation

from .models import Order
from .tests import CheckoutTestCase
from .views import stripe_message


class PortraitMessageTests(CheckoutTestCase):
    def make_portrait_order(self):
        order = Order.objects.create(user=self.user, status=Order.PAID, total=Decimal("30.00"))
        order.items.create(product_name="Portrait", option_name="Digital file",
                           product_type="portrait", price=Decimal("30.00"))
        return order

    def test_stripe_message_for_files_says_right_after_payment(self):
        message = stripe_message(self.make_order())
        self.assertIn("right after payment", message)

    def test_stripe_message_for_portrait_says_when_it_is_ready(self):
        message = stripe_message(self.make_portrait_order())
        self.assertIn("within 7 days", message)
        self.assertNotIn("right after payment", message)

    def test_confirmation_email_explains_the_portrait(self):
        mail.outbox = []
        send_order_confirmation(self.make_portrait_order())
        self.assertIn("within 7 days", mail.outbox[0].body)
        self.assertIn("within 7 days", mail.outbox[0].alternatives[0][0])
