"""Tests: a product can show example pictures, for example finished portraits (US-05)."""
import shutil
import tempfile
from decimal import Decimal

from django.test import TestCase, override_settings

from checkout.test_brief import photo
from products.models import Category, Product, ProductImage

TEST_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA)
class ProductExampleTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        category = Category.objects.create(name="Portraits", slug="portraits")
        self.portrait = Product.objects.create(
            category=category, name="Custom Portrait", description="Portrait.",
            price=Decimal("30.00"), product_type=Product.PORTRAIT, image=photo("poster.png"),
        )

    def test_examples_show_on_the_product_page(self):
        ProductImage.objects.create(product=self.portrait, image=photo("philipp-luca.png"),
                                    caption="Philipp and Luca")
        response = self.client.get(self.portrait.get_absolute_url())
        self.assertContains(response, "作品例子 Examples")
        self.assertContains(response, "Philipp and Luca")

    def test_no_examples_no_heading(self):
        response = self.client.get(self.portrait.get_absolute_url())
        self.assertNotContains(response, "作品例子 Examples")
