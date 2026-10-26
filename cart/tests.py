from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product


class CartTests(TestCase):
    """US-07, US-08 and US-09: add, remove, update and a correct total."""

    def setUp(self):
        category = Category.objects.create(name="Shop", slug="shop")
        self.stickers = Product.objects.create(
            category=category, name="Milk Tea Stickers", description="Stickers.",
            price=Decimal("4.50"), product_type=Product.DIGITAL,
        )
        self.tote = Product.objects.create(
            category=category, name="Tote Bag", description="A bag.",
            price=Decimal("18.00"), product_type=Product.PRINTED, stock=3,
        )
        self.sold_out = Product.objects.create(
            category=category, name="Postcards", description="Cards.",
            price=Decimal("6.00"), product_type=Product.PRINTED, stock=0,
        )

    def add(self, product, quantity=1):
        return self.client.post(reverse("cart:add", args=[product.pk]), {"quantity": quantity})

    def cart(self):
        return self.client.session.get("cart", {})

    def test_empty_cart_page(self):
        response = self.client.get(reverse("cart:detail"))
        self.assertContains(response, "Your cart is empty")

    def test_add_product_to_cart(self):
        response = self.add(self.stickers)
        self.assertRedirects(response, reverse("cart:detail"))
        self.assertEqual(self.cart(), {str(self.stickers.pk): 1})

    def test_digital_product_is_never_added_twice(self):
        self.add(self.stickers)
        self.add(self.stickers)
        self.assertEqual(self.cart()[str(self.stickers.pk)], 1)

    def test_printed_quantity_stops_at_stock(self):
        self.add(self.tote, quantity=10)
        self.assertEqual(self.cart()[str(self.tote.pk)], 3)

    def test_sold_out_product_cannot_be_added(self):
        self.add(self.sold_out)
        self.assertEqual(self.cart(), {})

    def test_hidden_product_cannot_be_added(self):
        self.stickers.is_active = False
        self.stickers.save()
        response = self.add(self.stickers)
        self.assertEqual(response.status_code, 404)

    def test_add_needs_post(self):
        response = self.client.get(reverse("cart:add", args=[self.stickers.pk]))
        self.assertEqual(response.status_code, 405)

    def test_remove_product(self):
        self.add(self.stickers)
        self.client.post(reverse("cart:remove", args=[self.stickers.pk]))
        self.assertEqual(self.cart(), {})

    def test_update_quantity(self):
        self.add(self.tote)
        self.client.post(reverse("cart:update", args=[self.tote.pk]), {"quantity": 2})
        self.assertEqual(self.cart()[str(self.tote.pk)], 2)

    def test_update_to_zero_removes(self):
        self.add(self.tote)
        self.client.post(reverse("cart:update", args=[self.tote.pk]), {"quantity": 0})
        self.assertEqual(self.cart(), {})

    def test_total_is_calculated_from_database_prices(self):
        self.add(self.stickers)
        self.add(self.tote, quantity=2)
        response = self.client.get(reverse("cart:detail"))
        self.assertEqual(response.context["total"], Decimal("40.50"))

    def test_total_follows_a_price_change(self):
        self.add(self.stickers)
        self.stickers.price = Decimal("5.00")
        self.stickers.save()
        response = self.client.get(reverse("cart:detail"))
        self.assertEqual(response.context["total"], Decimal("5.00"))

    def test_navbar_shows_cart_count(self):
        self.add(self.tote, quantity=2)
        self.add(self.stickers)
        response = self.client.get(reverse("home:index"))
        self.assertEqual(response.context["cart_count"], 3)
