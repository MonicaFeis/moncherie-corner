import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Category, Product

TEST_MEDIA = tempfile.mkdtemp()


def make_product(category, **extra):
    """Create a product quickly for a test."""
    data = {
        "category": category,
        "name": "Milk Tea Stickers",
        "description": "Six milk tea stickers.",
        "price": "4.50",
        "product_type": Product.DIGITAL,
    }
    data.update(extra)
    return Product.objects.create(**data)


class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Sticker sets", slug="sticker-sets")

    def test_slug_is_made_from_the_name(self):
        product = make_product(self.category)
        self.assertEqual(product.slug, "milk-tea-stickers")

    def test_second_product_with_same_name_gets_a_new_slug(self):
        make_product(self.category)
        second = make_product(self.category)
        self.assertEqual(second.slug, "milk-tea-stickers-2")

    def test_printed_item_with_no_stock_is_sold_out(self):
        product = make_product(self.category, product_type=Product.PRINTED, stock=0)
        self.assertTrue(product.is_sold_out)

    def test_printed_item_with_stock_is_not_sold_out(self):
        product = make_product(self.category, product_type=Product.PRINTED, stock=3)
        self.assertFalse(product.is_sold_out)

    def test_digital_item_is_never_sold_out(self):
        product = make_product(self.category, stock=0)
        self.assertFalse(product.is_sold_out)


class ShopPageTests(TestCase):
    """US-04 and US-05: browse and view products."""

    def setUp(self):
        self.stickers = Category.objects.create(name="Sticker sets", slug="sticker-sets")
        self.prints = Category.objects.create(name="Prints", slug="prints")
        self.tea = make_product(self.stickers)
        self.tote = make_product(self.prints, name="Tote Bag", product_type=Product.PRINTED, stock=5)
        self.hidden = make_product(self.stickers, name="Secret Set", is_active=False)

    def test_shop_lists_active_products_only(self):
        response = self.client.get(reverse("products:list"))
        self.assertContains(response, "Milk Tea Stickers")
        self.assertContains(response, "Tote Bag")
        self.assertNotContains(response, "Secret Set")

    def test_shop_filters_by_category(self):
        response = self.client.get(reverse("products:list") + "?category=prints")
        self.assertContains(response, "Tote Bag")
        self.assertNotContains(response, "Milk Tea Stickers")

    def test_unknown_category_gives_404(self):
        response = self.client.get(reverse("products:list") + "?category=nope")
        self.assertEqual(response.status_code, 404)

    def test_product_page_shows_details(self):
        response = self.client.get(self.tea.get_absolute_url())
        self.assertContains(response, "Milk Tea Stickers")
        self.assertContains(response, "4.50")

    def test_hidden_product_page_gives_404(self):
        response = self.client.get(self.hidden.get_absolute_url())
        self.assertEqual(response.status_code, 404)


@override_settings(MEDIA_ROOT=TEST_MEDIA)
class OwnerPageTests(TestCase):
    """US-18 to US-21: only the owner can add, edit and delete."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.category = Category.objects.create(name="Sticker sets", slug="sticker-sets")
        self.owner = User.objects.create_user("owner", "owner@example.com", "pass-12345!", is_staff=True)
        self.customer = User.objects.create_user("customer", "c@example.com", "pass-12345!")

    def form_data(self, **extra):
        data = {
            "name": "Dim Sum Stickers",
            "category": self.category.pk,
            "product_type": Product.DIGITAL,
            "price": "5.00",
            "description": "Eight dim sum stickers.",
            "stock": 0,
            "is_active": "on",
            "download_file": SimpleUploadedFile("dimsum.zip", b"zip-content"),
        }
        data.update(extra)
        return data

    def test_visitor_is_sent_to_login(self):
        response = self.client.get(reverse("products:manage"))
        self.assertRedirects(response, reverse("accounts:login") + "?next=" + reverse("products:manage"))

    def test_customer_is_forbidden(self):
        self.client.login(username="customer", password="pass-12345!")
        response = self.client.get(reverse("products:manage"))
        self.assertEqual(response.status_code, 403)

    def test_owner_can_open_manage_page(self):
        self.client.login(username="owner", password="pass-12345!")
        response = self.client.get(reverse("products:manage"))
        self.assertEqual(response.status_code, 200)

    def test_owner_can_add_a_product(self):
        self.client.login(username="owner", password="pass-12345!")
        response = self.client.post(reverse("products:add"), self.form_data())
        self.assertRedirects(response, reverse("products:manage"))
        self.assertTrue(Product.objects.filter(name="Dim Sum Stickers").exists())

    def test_price_must_be_above_zero(self):
        self.client.login(username="owner", password="pass-12345!")
        self.client.post(reverse("products:add"), self.form_data(price="0"))
        self.assertFalse(Product.objects.exists())

    def test_digital_product_needs_a_download_file(self):
        self.client.login(username="owner", password="pass-12345!")
        data = self.form_data()
        del data["download_file"]
        response = self.client.post(reverse("products:add"), data)
        self.assertContains(response, "needs a file to download")
        self.assertFalse(Product.objects.exists())

    def test_owner_can_edit_a_product(self):
        product = make_product(self.category, download_file="downloads/x.zip")
        self.client.login(username="owner", password="pass-12345!")
        data = self.form_data(name="New Name")
        del data["download_file"]
        self.client.post(reverse("products:edit", args=[product.pk]), data)
        product.refresh_from_db()
        self.assertEqual(product.name, "New Name")

    def test_delete_asks_first_then_deletes(self):
        product = make_product(self.category)
        self.client.login(username="owner", password="pass-12345!")
        response = self.client.get(reverse("products:delete", args=[product.pk]))
        self.assertContains(response, "Are you sure")
        self.assertTrue(Product.objects.exists())
        self.client.post(reverse("products:delete", args=[product.pk]))
        self.assertFalse(Product.objects.exists())

    def test_customer_cannot_delete(self):
        product = make_product(self.category)
        self.client.login(username="customer", password="pass-12345!")
        response = self.client.post(reverse("products:delete", args=[product.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Product.objects.exists())
