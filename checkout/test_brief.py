"""Tests for the portrait brief: number of people and reference photos (US-22, US-23)."""
from decimal import Decimal
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from cart.cart import make_key, split_key
from products.models import Product, ProductOption

from .models import Order
from .payments import mark_order_failed
from .tests import CheckoutTestCase, fake_session


def photo(name="me.png"):
    """A tiny real picture, made in memory."""
    buffer = BytesIO()
    Image.new("RGB", (10, 10), "teal").save(buffer, "PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


class PortraitBriefTests(CheckoutTestCase):
    def setUp(self):
        super().setUp()
        self.portrait = Product.objects.create(
            category=self.stickers.category, name="Portrait", description="Your portrait.",
            price=Decimal("30.00"), product_type=Product.PORTRAIT,
            max_people=4, extra_person_price=Decimal("10.00"),
        )
        self.digital = ProductOption.objects.create(product=self.portrait, name="Digital file")

    def add_portrait(self, people=1):
        self.client.post(
            reverse("cart:add", args=[self.portrait.pk]), {"option": self.digital.pk, "people": people}
        )

    def pay(self, data):
        with patch_stripe():
            return self.client.post(reverse("checkout:checkout"), data)

    def test_cart_keys_keep_option_and_people(self):
        self.assertEqual(split_key(make_key(self.portrait, self.digital, 3)), (self.portrait.pk, self.digital.pk, 3))
        self.assertEqual(split_key(make_key(self.portrait)), (self.portrait.pk, None, 1))

    def test_extra_people_add_to_the_price(self):
        self.add_portrait(people=3)
        response = self.client.get(reverse("cart:detail"))
        self.assertEqual(response.context["total"], Decimal("50.00"))
        self.assertContains(response, "3 people")

    def test_people_cannot_go_above_the_maximum(self):
        self.add_portrait(people=99)
        line = self.client.get(reverse("cart:detail")).context["lines"][0]
        self.assertEqual(line["people"], 4)

    def test_product_page_shows_people_choice(self):
        response = self.client.get(self.portrait.get_absolute_url())
        self.assertContains(response, "How many people")

    def test_portrait_checkout_needs_a_photo(self):
        self.add_portrait()
        response = self.pay({"notes": "My cat and me"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())

    def test_photos_and_people_are_saved_with_the_order(self):
        self.add_portrait(people=2)
        self.pay({"notes": "My cat and me", "reference_photos": [photo("a.png"), photo("b.png")]})
        order = Order.objects.get()
        self.assertEqual(order.reference_photos.count(), 2)
        item = order.items.get()
        self.assertEqual(item.people, 2)
        self.assertEqual(item.price, Decimal("40.00"))
        self.assertIn("2 people", item.display_name)

    def test_a_file_that_is_not_a_picture_is_refused(self):
        self.add_portrait()
        fake = SimpleUploadedFile("me.png", b"not a picture", content_type="image/png")
        response = self.pay({"notes": "Hi", "reference_photos": [fake]})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())

    def test_too_many_photos_are_refused(self):
        self.add_portrait()
        photos = [photo(f"{n}.png") for n in range(6)]
        self.pay({"notes": "Hi", "reference_photos": photos})
        self.assertFalse(Order.objects.exists())

    def test_photos_are_deleted_when_payment_fails(self):
        self.add_portrait()
        self.pay({"notes": "Hi", "reference_photos": [photo()]})
        order = Order.objects.get()
        mark_order_failed(order.pk)
        self.assertEqual(order.reference_photos.count(), 0)


def patch_stripe():
    from unittest.mock import patch
    return patch("checkout.views.stripe.checkout.Session.create", return_value=fake_session())
