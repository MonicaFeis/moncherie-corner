from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product


class BagMessageTests(TestCase):
    """The "already in your bag" message shows a shopping bag icon."""

    def setUp(self):
        category = Category.objects.create(name="Shop", slug="shop")
        self.stickers = Product.objects.create(
            category=category, name="Milk Tea Stickers", description="Stickers.",
            price=Decimal("4.50"), product_type=Product.DIGITAL,
        )

    def add_twice(self):
        url = reverse("cart:add", args=[self.stickers.pk])
        self.client.post(url, {"quantity": 1})
        return self.client.post(url, {"quantity": 1}, follow=True)

    def test_already_in_bag_shows_bag_icon(self):
        response = self.add_twice()
        self.assertContains(response, "is already in your bag")
        self.assertContains(response, "fa-bag-shopping")
        self.assertNotContains(response, "fa-bell-concierge")

    def test_message_keeps_the_info_colour_class(self):
        response = self.add_twice()
        self.assertContains(response, "alert-info")
        self.assertNotContains(response, "alert-bag")
