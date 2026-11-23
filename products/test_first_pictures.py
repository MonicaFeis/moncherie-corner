"""Tests: the first product pictures load straight away, the others load later."""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product


class FirstPicturesTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Stickers", slug="stickers")
        for number in range(4):
            Product.objects.create(
                category=category, name=f"Sticker set {number}", description="Stickers.",
                price=Decimal("4.50"), image="products/stickers.jpg",
            )

    def test_first_two_pictures_load_first(self):
        response = self.client.get(reverse("products:list"))
        self.assertContains(response, 'fetchpriority="high"', count=2)

    def test_other_pictures_wait(self):
        response = self.client.get(reverse("products:list"))
        self.assertContains(response, 'loading="lazy"', count=2)
