"""Tests: the home page has a Custom Portrait section with the poster (US-22)."""
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product


class PortraitSectionTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Portraits", slug="portraits")

    def test_section_shows_the_poster_and_links_to_the_portrait(self):
        portrait = Product.objects.create(
            category=self.category, name="Custom Portrait", description="Portrait.",
            price="30.00", product_type=Product.PORTRAIT,
        )
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, 'aria-labelledby="portrait-title"')
        self.assertContains(response, "images/customize-portrait.jpg")
        self.assertContains(response, f'href="{portrait.get_absolute_url()}" class="btn btn-shop"')

    def test_no_section_when_there_is_no_portrait_product(self):
        response = self.client.get(reverse("home:index"))
        self.assertNotContains(response, "images/customize-portrait.jpg")
