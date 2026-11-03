"""Tests: the home page carousel shows the products the owner chose (featured)."""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from products.forms import ProductForm
from products.models import Category, Product


class CarouselTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Stickers", slug="stickers")

    def make(self, name, **extra):
        return Product.objects.create(category=self.category, name=name, description="x.",
                                      price=Decimal("4.50"), **extra)

    def test_featured_products_are_in_the_carousel(self):
        self.make("Egg Tart Stickers", is_featured=True)
        self.make("Plain Postcard")
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, 'id="featured-track"')
        self.assertContains(response, "Egg Tart Stickers")
        self.assertNotContains(response, "Plain Postcard")

    def test_without_featured_products_the_newest_are_shown(self):
        self.make("Newest Sticker Set")
        self.assertContains(self.client.get(reverse("home:index")), "Newest Sticker Set")

    def test_hidden_products_are_never_featured(self):
        self.make("Secret Set", is_featured=True, is_active=False)
        self.assertNotContains(self.client.get(reverse("home:index")), "Secret Set")

    def test_carousel_script_is_loaded(self):
        self.make("Egg Tart Stickers", is_featured=True)
        self.assertContains(self.client.get(reverse("home:index")), "js/carousel.js")

    def test_owner_can_choose_featured_products(self):
        self.assertIn("is_featured", ProductForm().fields)
