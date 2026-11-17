"""Tests: the thank-you page only shows My downloads when there is a file to download now."""
from decimal import Decimal

from django.urls import reverse

from checkout.models import Order
from products.models import Product

from .tests import CheckoutTestCase


class ThankYouButtonTests(CheckoutTestCase):
    def setUp(self):
        super().setUp()
        self.portrait = Product.objects.create(
            category=self.stickers.category, name="Custom Portrait", description="A portrait.",
            price=Decimal("30.00"), product_type=Product.PORTRAIT, stock=4,
        )

    def paid_order(self, product, session_id):
        order = Order.objects.create(user=self.user, status=Order.PAID, total=product.price,
                                     stripe_session_id=session_id)
        order.items.create(product=product, product_name=product.name,
                           product_type=product.product_type, price=product.price)
        return order

    def thank_you_page(self, session_id):
        return self.client.get(reverse("checkout:success") + f"?session_id={session_id}")

    def test_portrait_only_order_has_no_downloads_button(self):
        self.paid_order(self.portrait, "cs_test_portrait")
        response = self.thank_you_page("cs_test_portrait")
        self.assertContains(response, "I'll start drawing your portrait")
        self.assertNotContains(response, "我的下載 My downloads")

    def test_digital_order_has_downloads_button(self):
        self.paid_order(self.stickers, "cs_test_digital")
        response = self.thank_you_page("cs_test_digital")
        self.assertContains(response, "我的下載 My downloads")
