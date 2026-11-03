"""Tests: the hero button "Commission a portrait" opens the portrait order page."""
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product


class PortraitButtonTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Portraits", slug="portraits")

    def test_button_opens_the_portrait_product(self):
        portrait = Product.objects.create(
            category=self.category, name="Custom Portrait", description="Portrait.",
            price="30.00", product_type=Product.PORTRAIT,
        )
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, f'href="{portrait.get_absolute_url()}" class="btn btn-shop-outline ms-2"')

    def test_without_a_portrait_the_button_opens_the_portraits_category(self):
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, "?category=portraits")
