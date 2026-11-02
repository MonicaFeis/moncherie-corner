"""Tests for My downloads after a portrait order, and the portrait order form (US-15, US-23, US-24)."""
from decimal import Decimal

from django.urls import reverse

from products.models import Product, ProductOption

from .models import Order
from .test_brief import photo
from .tests import CheckoutTestCase


class DownloadsAfterPortraitOrderTests(CheckoutTestCase):
    def setUp(self):
        super().setUp()
        self.portrait = Product.objects.create(
            category=self.stickers.category, name="Custom Portrait", description="Portrait.",
            price=Decimal("30.00"), product_type=Product.PORTRAIT, image=photo("example.png"),
        )
        self.sticker_order = self.make_order(status=Order.PAID)
        self.portrait_order = Order.objects.create(user=self.user, status=Order.PAID, total=Decimal("30.00"))
        self.portrait_order.items.create(product=self.portrait, product_name="Custom Portrait",
                                         product_type="portrait", price=Decimal("30.00"))

    def test_one_order_shows_only_its_own_items(self):
        url = reverse("checkout:my_downloads") + f"?order={self.portrait_order.pk}"
        response = self.client.get(url)
        self.assertContains(response, "Custom Portrait")
        self.assertNotContains(response, "Milk Tea Stickers")
        self.assertContains(response, "See all my downloads")

    def test_without_an_order_all_downloads_show(self):
        response = self.client.get(reverse("checkout:my_downloads"))
        self.assertContains(response, "Custom Portrait")
        self.assertContains(response, "Milk Tea Stickers")

    def test_waiting_portrait_always_shows_the_being_drawn_picture(self):
        response = self.client.get(reverse("checkout:my_downloads"))
        self.assertContains(response, "images/being-drawn.png")
        self.assertContains(response, f"Order #{self.portrait_order.pk}")

    def test_portrait_checkout_asks_for_names(self):
        option = ProductOption.objects.create(product=self.portrait, name="Digital file")
        self.client.post(reverse("cart:add", args=[self.portrait.pk]), {"option": option.pk})
        response = self.client.get(reverse("checkout:checkout"))
        self.assertContains(response, "Names")
        self.assertContains(response, "Photos")
