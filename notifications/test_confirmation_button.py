"""Tests: the confirmation email only has a download button when there is a file to download now (US-30)."""
from decimal import Decimal

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from checkout.models import Order
from notifications.emails import send_order_confirmation


class ConfirmationButtonTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("rosa", "rosa@example.com", "pass-12345!")
        mail.outbox = []

    def send(self, *product_types):
        order = Order.objects.create(user=self.user, status=Order.PAID, total=Decimal("10.00"))
        for product_type in product_types:
            order.items.create(product_name="Item", product_type=product_type, price=Decimal("5.00"))
        send_order_confirmation(order)
        message = mail.outbox[-1]
        return order, message.body, message.alternatives[0][0]

    def test_digital_files_get_the_download_button(self):
        order, text, html = self.send("digital")
        self.assertIn(reverse("checkout:my_downloads"), html)
        self.assertIn(reverse("checkout:my_downloads"), text)

    def test_portrait_only_gets_see_your_order_instead(self):
        order, text, html = self.send("portrait")
        self.assertNotIn(reverse("checkout:my_downloads"), html)
        self.assertNotIn(reverse("checkout:my_downloads"), text)
        self.assertIn(order.get_absolute_url(), html)

    def test_printed_only_gets_see_your_order_instead(self):
        order, text, html = self.send("printed")
        self.assertNotIn(reverse("checkout:my_downloads"), html)
        self.assertIn(order.get_absolute_url(), html)

    def test_portrait_and_stickers_get_the_download_button(self):
        order, text, html = self.send("portrait", "digital")
        self.assertIn(reverse("checkout:my_downloads"), html)
