from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product


class BagMessageTests(TestCase):
    """Messages about the bag show a shopping bag icon, in the shop's colours."""

    def setUp(self):
        category = Category.objects.create(name="Shop", slug="shop")
        self.stickers = Product.objects.create(
            category=category, name="Milk Tea Stickers", description="Stickers.",
            price=Decimal("4.50"), product_type=Product.DIGITAL,
        )
        self.url = reverse("cart:add", args=[self.stickers.pk])

    def test_added_to_bag_shows_bag_icon(self):
        response = self.client.post(self.url, {"quantity": 1}, follow=True)
        self.assertContains(response, "Added Milk Tea Stickers to your bag")
        self.assertContains(response, "fa-bag-shopping")
        self.assertNotContains(response, "alert-emoji")

    def test_already_in_bag_shows_bag_icon(self):
        self.client.post(self.url, {"quantity": 1})
        response = self.client.post(self.url, {"quantity": 1}, follow=True)
        self.assertContains(response, "is already in your bag")
        self.assertContains(response, "fa-bag-shopping")
        self.assertNotContains(response, "fa-bell-concierge")

    def test_message_keeps_its_colour_class(self):
        self.client.post(self.url, {"quantity": 1})
        response = self.client.post(self.url, {"quantity": 1}, follow=True)
        self.assertContains(response, "alert-info")
        self.assertNotContains(response, "alert-bag")
