"""Tests: the home page shows a few recent happy reviews (US-16)."""
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product
from reviews.models import Review


class HomeReviewTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Stickers", slug="stickers")
        self.product = Product.objects.create(category=category, name="Milk Tea Stickers",
                                              description="Stickers.", price=Decimal("4.50"))
        self.rosa = User.objects.create_user("rosa", "rosa@example.com", "pass-12345!")
        self.luca = User.objects.create_user("luca", "luca@example.com", "pass-12345!")

    def test_recent_happy_reviews_are_shown(self):
        Review.objects.create(product=self.product, user=self.rosa, rating=5, comment="So cute on my laptop")
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, "客人話 What customers say")
        self.assertContains(response, "So cute on my laptop")
        self.assertContains(response, self.product.get_absolute_url())

    def test_low_ratings_are_not_featured(self):
        Review.objects.create(product=self.product, user=self.luca, rating=2, comment="Too small")
        self.assertNotContains(self.client.get(reverse("home:index")), "Too small")

    def test_no_reviews_no_section(self):
        self.assertNotContains(self.client.get(reverse("home:index")), "客人話 What customers say")
