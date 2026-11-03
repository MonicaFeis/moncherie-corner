"""Tests: downloads are available for 30 days, and the owner has an Orders link (US-15, US-24, US-36)."""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils import timezone

from .models import Order
from .tests import PASSWORD, CheckoutTestCase


class DownloadExpiryTests(CheckoutTestCase):
    def days_ago(self, order, days):
        Order.objects.filter(pk=order.pk).update(created_at=timezone.now() - timedelta(days=days))

    def test_new_download_shows_until_when(self):
        self.make_order(status=Order.PAID)
        response = self.client.get(reverse("checkout:my_downloads"))
        self.assertContains(response, "Milk Tea Stickers")
        self.assertContains(response, "Available until")

    def test_download_older_than_30_days_disappears(self):
        order = self.make_order(status=Order.PAID)
        self.days_ago(order, 31)
        response = self.client.get(reverse("checkout:my_downloads"))
        self.assertNotContains(response, "Milk Tea Stickers")
        download = self.client.get(reverse("checkout:download", args=[self.stickers.pk]))
        self.assertEqual(download.status_code, 404)

    def test_portrait_older_than_30_days_after_delivery_disappears(self):
        order = Order.objects.create(user=self.user, status=Order.PAID, total=Decimal("30.00"))
        item = order.items.create(product_name="Portrait", product_type="portrait", price=Decimal("30.00"))
        item.delivered_file.save("rosa.png", ContentFile(b"png"))
        item.delivered_at = timezone.now() - timedelta(days=31)
        item.save()
        response = self.client.get(reverse("checkout:my_downloads"))
        self.assertNotContains(response, "Download portrait")
        download = self.client.get(reverse("checkout:download_portrait", args=[item.pk]))
        self.assertEqual(download.status_code, 404)

    def test_owner_has_an_orders_link_in_the_menu(self):
        User.objects.create_user("owner", "owner@example.com", PASSWORD, is_staff=True)
        self.client.login(username="owner", password=PASSWORD)
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, f'href="{reverse("checkout:manage_orders")}"')

    def test_customer_has_no_orders_management_link(self):
        response = self.client.get(reverse("home:index"))
        self.assertNotContains(response, f'href="{reverse("checkout:manage_orders")}"')
