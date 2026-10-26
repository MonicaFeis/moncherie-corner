import shutil
import tempfile
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import mail
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.urls import reverse

from products.models import Category, Product

from .models import Order, ShippingMethod
from .payments import mark_order_failed, mark_order_paid

TEST_MEDIA = tempfile.mkdtemp()
PASSWORD = "pass-12345!"


def fake_session(session_id="cs_test_1", url="https://checkout.stripe.com/pay/test"):
    return SimpleNamespace(id=session_id, url=url)


@override_settings(MEDIA_ROOT=TEST_MEDIA, STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x")
class CheckoutTestCase(TestCase):
    """Shared set-up: a customer, a digital product and a printed product."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user("cherry", "cherry@example.com", PASSWORD)
        self.other = User.objects.create_user("other", "other@example.com", PASSWORD)
        category = Category.objects.create(name="Shop", slug="shop")
        self.stickers = Product.objects.create(
            category=category, name="Milk Tea Stickers", description="Stickers.",
            price=Decimal("4.50"), product_type=Product.DIGITAL,
        )
        self.stickers.download_file.save("milktea.zip", ContentFile(b"zip-data"))
        self.tote = Product.objects.create(
            category=category, name="Tote Bag", description="A bag.",
            price=Decimal("18.00"), product_type=Product.PRINTED, stock=3,
        )
        self.post = ShippingMethod.objects.create(name="Standard post", price=Decimal("3.90"), delivery_days=5)
        self.client.login(username="cherry", password=PASSWORD)

    def add_to_cart(self, product, quantity=1):
        self.client.post(reverse("cart:add", args=[product.pk]), {"quantity": quantity})

    def make_order(self, user=None, status=Order.PENDING, product=None):
        product = product or self.stickers
        order = Order.objects.create(user=user or self.user, status=status, total=product.price,
                                     stripe_session_id="cs_test_1")
        order.items.create(product=product, product_name=product.name,
                           product_type=product.product_type, price=product.price)
        return order


class CheckoutPageTests(CheckoutTestCase):
    """US-10: going to Stripe."""

    def test_visitor_must_log_in(self):
        self.client.logout()
        response = self.client.get(reverse("checkout:checkout"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_empty_cart_goes_back_to_cart(self):
        response = self.client.get(reverse("checkout:checkout"))
        self.assertRedirects(response, reverse("cart:detail"))

    @patch("checkout.views.stripe.checkout.Session.create", return_value=fake_session())
    def test_digital_order_is_created_and_sent_to_stripe(self, create):
        self.add_to_cart(self.stickers)
        response = self.client.post(reverse("checkout:checkout"))
        self.assertRedirects(response, "https://checkout.stripe.com/pay/test", fetch_redirect_response=False)
        order = Order.objects.get()
        self.assertEqual(order.status, Order.PENDING)
        self.assertEqual(order.total, Decimal("4.50"))
        self.assertEqual(order.stripe_session_id, "cs_test_1")
        line = create.call_args.kwargs["line_items"][0]
        self.assertEqual(line["price_data"]["unit_amount"], 450)
        self.assertNotIn("shipping_address_collection", create.call_args.kwargs)

    def test_printed_item_needs_a_shipping_method(self):
        self.add_to_cart(self.tote)
        response = self.client.post(reverse("checkout:checkout"), {})
        self.assertContains(response, "Please choose how to ship")
        self.assertFalse(Order.objects.exists())

    @patch("checkout.views.stripe.checkout.Session.create", return_value=fake_session())
    def test_shipping_is_added_to_the_total(self, create):
        self.add_to_cart(self.tote, quantity=2)
        self.client.post(reverse("checkout:checkout"), {"shipping_method": self.post.pk})
        order = Order.objects.get()
        self.assertEqual(order.total, Decimal("39.90"))
        self.assertIn("shipping_address_collection", create.call_args.kwargs)


class PaymentResultTests(CheckoutTestCase):
    """US-11, US-12, US-30 and US-40: what happens after Stripe."""

    def test_paid_order_lowers_stock_once_and_sends_one_email(self):
        order = self.make_order(product=self.tote)
        order.items.update(quantity=2)
        self.assertTrue(mark_order_paid(order.pk))
        self.assertFalse(mark_order_paid(order.pk))
        self.tote.refresh_from_db()
        self.assertEqual(self.tote.stock, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Order confirmed", mail.outbox[0].subject)

    @patch("checkout.views.stripe.checkout.Session.retrieve")
    def test_success_page_checks_stripe_and_clears_cart(self, retrieve):
        retrieve.return_value = {"payment_status": "paid"}
        self.add_to_cart(self.stickers)
        order = self.make_order()
        response = self.client.get(reverse("checkout:success") + "?session_id=cs_test_1")
        order.refresh_from_db()
        self.assertEqual(order.status, Order.PAID)
        self.assertContains(response, "Thank you for your order")
        self.assertEqual(self.client.session.get("cart"), {})

    @patch("checkout.views.stripe.checkout.Session.retrieve")
    def test_unpaid_session_is_not_marked_paid(self, retrieve):
        retrieve.return_value = {"payment_status": "unpaid"}
        order = self.make_order()
        self.client.get(reverse("checkout:success") + "?session_id=cs_test_1")
        order.refresh_from_db()
        self.assertEqual(order.status, Order.PENDING)

    def test_cancel_marks_order_cancelled_and_keeps_cart(self):
        self.add_to_cart(self.stickers)
        order = self.make_order()
        response = self.client.get(reverse("checkout:cancelled", args=[order.pk]))
        order.refresh_from_db()
        self.assertEqual(order.status, Order.CANCELLED)
        self.assertContains(response, "didn't go through")
        self.assertTrue(self.client.session.get("cart"))
        self.assertIn("Payment not completed", mail.outbox[0].subject)

    def test_failed_email_is_only_sent_once(self):
        order = self.make_order()
        mark_order_failed(order.pk)
        mark_order_failed(order.pk)
        self.assertEqual(len(mail.outbox), 1)

    def test_cannot_cancel_someone_elses_order(self):
        order = self.make_order(user=self.other)
        response = self.client.get(reverse("checkout:cancelled", args=[order.pk]))
        self.assertEqual(response.status_code, 404)


class WebhookTests(CheckoutTestCase):
    """US-13: only real Stripe messages can change an order."""

    def post_webhook(self):
        return self.client.post(reverse("checkout:webhook"), data=b"{}",
                                content_type="application/json", HTTP_STRIPE_SIGNATURE="t=1,v1=x")

    def test_bad_signature_is_rejected(self):
        response = self.post_webhook()
        self.assertEqual(response.status_code, 400)

    @patch("checkout.views.stripe.Webhook.construct_event")
    def test_completed_event_marks_order_paid(self, construct):
        order = self.make_order()
        construct.return_value = {"type": "checkout.session.completed", "data": {"object": {
            "payment_status": "paid", "metadata": {"order_id": str(order.pk)}}}}
        response = self.post_webhook()
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.PAID)

    @patch("checkout.views.stripe.Webhook.construct_event")
    def test_expired_event_marks_order_expired(self, construct):
        order = self.make_order()
        construct.return_value = {"type": "checkout.session.expired", "data": {"object": {
            "metadata": {"order_id": str(order.pk)}}}}
        self.post_webhook()
        order.refresh_from_db()
        self.assertEqual(order.status, Order.EXPIRED)


class OrdersAndDownloadsTests(CheckoutTestCase):
    """US-14, US-15 and US-31."""

    def test_my_orders_shows_only_my_orders(self):
        mine = self.make_order()
        theirs = self.make_order(user=self.other)
        response = self.client.get(reverse("checkout:my_orders"))
        self.assertContains(response, f"#{mine.pk}")
        self.assertNotContains(response, f"#{theirs.pk}<")

    def test_order_detail_of_someone_else_is_404(self):
        theirs = self.make_order(user=self.other)
        response = self.client.get(reverse("checkout:order_detail", args=[theirs.pk]))
        self.assertEqual(response.status_code, 404)

    def test_paid_customer_can_download(self):
        self.make_order(status=Order.PAID)
        response = self.client.get(reverse("checkout:download", args=[self.stickers.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"zip-data")

    def test_unpaid_order_cannot_download(self):
        self.make_order(status=Order.PENDING)
        response = self.client.get(reverse("checkout:download", args=[self.stickers.pk]))
        self.assertEqual(response.status_code, 404)

    def test_other_customers_cannot_download(self):
        self.make_order(user=self.other, status=Order.PAID)
        response = self.client.get(reverse("checkout:download", args=[self.stickers.pk]))
        self.assertEqual(response.status_code, 404)

    def test_downloads_page_lists_paid_files(self):
        self.make_order(status=Order.PAID)
        response = self.client.get(reverse("checkout:my_downloads"))
        self.assertContains(response, "Milk Tea Stickers")
