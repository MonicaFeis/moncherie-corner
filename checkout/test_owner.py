from decimal import Decimal

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product

from .models import Order

PASSWORD = "pass-12345!"


class OwnerOrderTests(TestCase):
    """US-36: the owner sees paid orders and marks printed ones as shipped."""

    def setUp(self):
        self.owner = User.objects.create_user("owner", "owner@example.com", PASSWORD, is_staff=True)
        self.customer = User.objects.create_user("cherry", "cherry@example.com", PASSWORD)
        category = Category.objects.create(name="Prints", slug="prints")
        self.tote = Product.objects.create(
            category=category, name="Tote Bag", description="A bag.",
            price=Decimal("18.00"), product_type=Product.PRINTED, stock=5,
        )
        self.stickers = Product.objects.create(
            category=category, name="Stickers", description="Stickers.",
            price=Decimal("4.50"), product_type=Product.DIGITAL,
        )
        self.print_order = self.make_order(self.tote, Order.PAID)
        self.digital_order = self.make_order(self.stickers, Order.PAID)
        self.waiting_order = self.make_order(self.tote, Order.PENDING)

    def make_order(self, product, status):
        order = Order.objects.create(user=self.customer, status=status, total=product.price)
        order.items.create(product=product, product_name=product.name,
                           product_type=product.product_type, price=product.price)
        return order

    def ship_url(self, order):
        return reverse("checkout:manage_order", args=[order.pk])

    def test_customer_cannot_see_owner_orders(self):
        self.client.login(username="cherry", password=PASSWORD)
        response = self.client.get(reverse("checkout:manage_orders"))
        self.assertEqual(response.status_code, 403)

    def test_visitor_is_sent_to_login(self):
        response = self.client.get(reverse("checkout:manage_orders"))
        self.assertEqual(response.status_code, 302)

    def test_owner_sees_all_orders(self):
        self.client.login(username="owner", password=PASSWORD)
        response = self.client.get(reverse("checkout:manage_orders"))
        self.assertContains(response, f"#{self.print_order.pk}")
        self.assertContains(response, f"#{self.digital_order.pk}")

    def test_to_ship_filter_shows_only_paid_printed_orders(self):
        self.client.login(username="owner", password=PASSWORD)
        response = self.client.get(reverse("checkout:manage_orders") + "?show=to_ship")
        orders = list(response.context["orders"])
        self.assertEqual(orders, [self.print_order])

    def test_mark_shipped_saves_tracking_and_emails_customer(self):
        self.client.login(username="owner", password=PASSWORD)
        response = self.client.post(self.ship_url(self.print_order), {"tracking_number": "DE123456789"})
        self.assertRedirects(response, self.ship_url(self.print_order))
        self.print_order.refresh_from_db()
        self.assertEqual(self.print_order.status, Order.SHIPPED)
        self.assertEqual(self.print_order.tracking_number, "DE123456789")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("shipped", mail.outbox[0].subject.lower())
        self.assertIn("DE123456789", mail.outbox[0].body)

    def test_tracking_number_is_required(self):
        self.client.login(username="owner", password=PASSWORD)
        response = self.client.post(self.ship_url(self.print_order), {"tracking_number": "  "})
        self.assertContains(response, "Please enter the tracking number")
        self.print_order.refresh_from_db()
        self.assertEqual(self.print_order.status, Order.PAID)

    def test_digital_order_cannot_be_shipped(self):
        self.client.login(username="owner", password=PASSWORD)
        self.client.post(self.ship_url(self.digital_order), {"tracking_number": "X1"})
        self.digital_order.refresh_from_db()
        self.assertEqual(self.digital_order.status, Order.PAID)
        self.assertEqual(len(mail.outbox), 0)

    def test_unpaid_order_cannot_be_shipped(self):
        self.client.login(username="owner", password=PASSWORD)
        self.client.post(self.ship_url(self.waiting_order), {"tracking_number": "X1"})
        self.waiting_order.refresh_from_db()
        self.assertEqual(self.waiting_order.status, Order.PENDING)

    def test_customer_sees_tracking_on_their_order(self):
        self.print_order.status = Order.SHIPPED
        self.print_order.tracking_number = "DE123456789"
        self.print_order.save()
        self.client.login(username="cherry", password=PASSWORD)
        response = self.client.get(self.print_order.get_absolute_url())
        self.assertContains(response, "DE123456789")
