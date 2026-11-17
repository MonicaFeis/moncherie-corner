"""Tests: lines starting with "## " in a product description become small headings."""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product
from products.templatetags.shop_text import description_html


class DescriptionHeadingTests(TestCase):
    def test_hash_line_becomes_heading(self):
        html = description_html("Intro text.\n\n## 價錢 Price\n• 1 person is €20.")
        self.assertIn('<h2 class="description-heading">價錢 Price</h2>', html)
        self.assertIn("• 1 person is €20.", html)
        self.assertNotIn("##", html)

    def test_text_without_headings_keeps_its_lines(self):
        html = description_html("Line one\nLine two")
        self.assertIn("Line one<br>Line two", html)
        self.assertNotIn("description-heading", html)

    def test_html_in_description_is_escaped(self):
        html = description_html("## <b>Hi</b>\n<script>alert(1)</script>")
        self.assertNotIn("<script>", html)
        self.assertNotIn("<b>", html)

    def test_product_page_shows_heading(self):
        category = Category.objects.create(name="Portraits", slug="portraits")
        product = Product.objects.create(
            category=category, name="Custom Portrait", description="Intro.\n\n## 價錢 Price\nFrom €20.",
            price=Decimal("20.00"), product_type=Product.PORTRAIT, stock=4,
        )
        response = self.client.get(reverse("products:detail", args=[product.slug]))
        self.assertContains(response, '<h2 class="description-heading">價錢 Price</h2>', html=False)
