"""Tests for portrait versions (digital or printed) and portrait delivery (US-22, US-24, US-42)."""
from decimal import Decimal

from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from products.models import Product, ProductOption

from .models import Order
from .tests import PASSWORD, CheckoutTestCase


class PortraitOptionsTests(CheckoutTestCase):
    def setUp(self):
        super().setUp()
        self.portrait = Product.objects.create(
            category=self.stickers.category, name="Portrait", description="Your portrait.",
            price=Decimal("30.00"), product_type=Product.PORTRAIT,
        )
        self.digital = ProductOption.objects.create(product=self.portrait, name="Digital file", position=1)
        self.printed = ProductOption.objects.create(
            product=self.portrait, name="Printed A4", extra_price=Decimal("10.00"), is_printed=True, position=2,
        )

    def add_portrait(self, option):
        return self.client.post(reverse("cart:add", args=[self.portrait.pk]), {"option": option.pk})

    def test_option_price_is_product_price_plus_extra(self):
        self.assertEqual(self.printed.price, Decimal("40.00"))

    def test_product_page_shows_the_choices(self):
        response = self.client.get(self.portrait.get_absolute_url())
        self.assertContains(response, "Choose your version")
        self.assertContains(response, "Printed A4")

    def test_a_version_must_be_chosen(self):
        self.client.post(reverse("cart:add", args=[self.portrait.pk]))
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_option_from_another_product_is_refused(self):
        other = ProductOption.objects.create(product=self.tote, name="Gift wrap")
        self.client.post(reverse("cart:add", args=[self.portrait.pk]), {"option": other.pk})
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_bag_uses_option_price(self):
        self.add_portrait(self.printed)
        response = self.client.get(reverse("cart:detail"))
        self.assertContains(response, "Printed A4")
        self.assertEqual(response.context["total"], Decimal("40.00"))

    def test_digital_and_printed_versions_are_separate_lines(self):
        self.add_portrait(self.digital)
        self.add_portrait(self.printed)
        self.assertEqual(len(self.client.get(reverse("cart:detail")).context["lines"]), 2)

    def test_remove_one_version(self):
        self.add_portrait(self.digital)
        key = f"{self.portrait.pk}:{self.digital.pk}"
        self.client.post(reverse("cart:remove", args=[key]))
        self.assertEqual(self.client.session["cart"], {})

    def test_digital_portrait_needs_no_shipping(self):
        self.add_portrait(self.digital)
        response = self.client.get(reverse("checkout:checkout"))
        self.assertFalse(response.context["form"].needs_shipping)

    def test_printed_portrait_needs_shipping(self):
        self.add_portrait(self.printed)
        response = self.client.get(reverse("checkout:checkout"))
        self.assertTrue(response.context["form"].needs_shipping)


class PortraitDeliveryTests(CheckoutTestCase):
    def setUp(self):
        super().setUp()
        self.owner = User.objects.create_user("owner", "owner@example.com", PASSWORD, is_staff=True)
        self.order = Order.objects.create(user=self.user, status=Order.PAID, total=Decimal("30.00"))
        self.item = self.order.items.create(
            product_name="Portrait", option_name="Digital file", product_type="portrait", price=Decimal("30.00"),
        )
        mail.outbox = []

    def deliver(self, file=None):
        self.client.login(username="owner", password=PASSWORD)
        file = file or SimpleUploadedFile("rosa.png", b"png-data", content_type="image/png")
        return self.client.post(
            reverse("checkout:manage_order", args=[self.order.pk]),
            {"action": "deliver", "item_id": self.item.pk, "portrait_file": file},
        )

    def test_display_name_shows_the_version(self):
        self.assertEqual(self.item.display_name, "Portrait (Digital file)")

    def test_paid_portrait_shows_as_being_drawn(self):
        response = self.client.get(reverse("checkout:my_downloads"))
        self.assertContains(response, "Being drawn")
        self.assertContains(response, "images/being-drawn.png")

    def test_owner_upload_saves_file_and_emails_customer(self):
        self.deliver()
        self.item.refresh_from_db()
        self.assertTrue(self.item.delivered_file)
        self.assertIsNotNone(self.item.delivered_at)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["cherry@example.com"])
        self.assertIn("portrait is ready", mail.outbox[0].subject)

    def test_wrong_file_type_is_refused(self):
        response = self.deliver(SimpleUploadedFile("virus.exe", b"x"))
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertFalse(self.item.delivered_file)
        self.assertEqual(len(mail.outbox), 0)

    def test_customer_cannot_deliver(self):
        file = SimpleUploadedFile("rosa.png", b"png-data")
        response = self.client.post(
            reverse("checkout:manage_order", args=[self.order.pk]),
            {"action": "deliver", "item_id": self.item.pk, "portrait_file": file},
        )
        self.assertEqual(response.status_code, 403)

    def test_customer_downloads_delivered_portrait(self):
        self.deliver()
        self.client.login(username="cherry", password=PASSWORD)
        self.assertContains(self.client.get(reverse("checkout:my_downloads")), "Download portrait")
        response = self.client.get(reverse("checkout:download_portrait", args=[self.item.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"png-data")

    def test_other_customer_cannot_download_portrait(self):
        self.deliver()
        self.client.login(username="other", password=PASSWORD)
        response = self.client.get(reverse("checkout:download_portrait", args=[self.item.pk]))
        self.assertEqual(response.status_code, 404)

    def test_to_draw_filter_lists_undelivered_portraits(self):
        self.client.login(username="owner", password=PASSWORD)
        response = self.client.get(reverse("checkout:manage_orders") + "?show=to_draw")
        self.assertIn(self.order, response.context["orders"])
