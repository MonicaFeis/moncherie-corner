"""Tests: a digital product with a printed version, like a postcard (US-17).

Buying the digital version unlocks the file. Buying the printed version
means it is posted, so it does not unlock the file.
"""
from django.urls import reverse

from checkout.models import Order
from products.models import ProductOption

from .tests import CheckoutTestCase


class PrintedVersionTests(CheckoutTestCase):
    def setUp(self):
        super().setUp()
        self.digital = ProductOption.objects.create(product=self.stickers, name="Digital file")
        self.printed = ProductOption.objects.create(
            product=self.stickers, name="Printed postcard", extra_price="1.50", is_printed=True,
        )

    def buy(self, option):
        order = Order.objects.create(user=self.user, status=Order.PAID, total=self.stickers.price,
                                     stripe_session_id=f"cs_test_{option.pk}")
        order.items.create(product=self.stickers, product_name=self.stickers.name,
                           product_type=self.stickers.product_type, price=self.stickers.price,
                           option_name=option.name, is_printed=option.is_printed)
        return order

    def test_digital_version_can_be_downloaded(self):
        self.buy(self.digital)
        response = self.client.get(reverse("checkout:download", args=[self.stickers.pk]))
        self.assertEqual(response.status_code, 200)

    def test_printed_version_cannot_be_downloaded(self):
        self.buy(self.printed)
        response = self.client.get(reverse("checkout:download", args=[self.stickers.pk]))
        self.assertEqual(response.status_code, 404)

    def test_printed_version_is_not_on_my_downloads(self):
        self.buy(self.printed)
        response = self.client.get(reverse("checkout:my_downloads"))
        self.assertNotContains(response, reverse("checkout:download", args=[self.stickers.pk]))

    def test_printed_only_order_has_no_files_to_download(self):
        order = self.buy(self.printed)
        self.assertFalse(order.has_files_to_download_now)
        self.assertFalse(order.has_digital_items)
