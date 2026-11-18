"""Tests: headings go in order (h1, h2, h3) so the W3C HTML checker is happy."""
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product
from reviews.models import Review


class HeadingOrderTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Stickers", slug="stickers")
        self.product = Product.objects.create(
            category=category, name="Milk Tea Stickers", description="Stickers.", price=Decimal("4.50"),
        )

    def test_product_list_has_h2_before_product_cards(self):
        response = self.client.get(reverse("products:list"))
        html = response.content.decode()
        self.assertIn('<h2 class="visually-hidden">商品 Products</h2>', html)
        self.assertLess(html.index("visually-hidden\">商品 Products"), html.index('class="product-name"'))

    def test_each_review_has_a_heading(self):
        buyer = User.objects.create_user("rosa", "rosa@example.com", "pass-12345!")
        Review.objects.create(product=self.product, user=buyer, rating=5, comment="Lovely")
        response = self.client.get(self.product.get_absolute_url())
        self.assertContains(response, '<h3 class="review-author h6 mb-0">rosa</h3>', html=False)
