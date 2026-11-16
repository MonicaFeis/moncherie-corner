"""Tests for the hand-drawn shop signs on the error, empty and status pages (US-46)."""
from decimal import Decimal

from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse

from checkout.models import Order
from products.models import Category

PASSWORD = "a-safe-test-password-123"


class SignPagesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("rosa", "rosa@example.com", PASSWORD)

    def test_home_hero_uses_the_welcome_poster(self):
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, "images/hero-poster.webp")
        self.assertContains(response, "images/hero-poster.jpg")

    def test_404_page_shows_the_offline_sign(self):
        response = self.client.get("/this-page-does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "images/sign-404.png", status_code=404)
        self.assertContains(response, reverse("home:index"), status_code=404)

    def test_403_page_shows_the_mind_your_own_business_sign(self):
        self.client.login(username="rosa", password=PASSWORD)
        response = self.client.get(reverse("products:manage"))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "images/sign-403.png", status_code=403)

    def test_500_page_shows_the_busy_sign(self):
        html = render_to_string("500.html")
        self.assertIn("images/sign-500.png", html)
        self.assertIn("Back to the home page", html)

    def test_empty_bag_shows_the_take_a_break_sign(self):
        response = self.client.get(reverse("cart:detail"))
        self.assertContains(response, "images/sign-empty-cart.png")

    def test_logging_out_shows_the_go_home_sign(self):
        self.client.login(username="rosa", password=PASSWORD)
        response = self.client.post(reverse("accounts:logout"), follow=True)
        self.assertContains(response, "images/sign-logout.png")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_paid_order_shows_the_thank_you_sign(self):
        order = Order.objects.create(user=self.user, status=Order.PAID,
                                     total=Decimal("4.50"), stripe_session_id="cs_test_sign")
        self.client.login(username="rosa", password=PASSWORD)
        response = self.client.get(reverse("checkout:success") + "?session_id=cs_test_sign")
        self.assertContains(response, "images/sign-thank-you.png")
        self.assertContains(response, f"#{order.pk}")

    def test_failed_payment_shows_the_oops_sign(self):
        order = Order.objects.create(user=self.user, total=Decimal("4.50"))
        self.client.login(username="rosa", password=PASSWORD)
        response = self.client.get(reverse("checkout:cancelled", args=[order.pk]))
        self.assertContains(response, "images/sign-payment-failed.png")

    def test_empty_category_shows_the_keep_going_sign(self):
        Category.objects.create(name="Coming soon", slug="coming-soon")
        response = self.client.get(reverse("products:list") + "?category=coming-soon")
        self.assertContains(response, "images/sign-no-results.png")

    def test_no_orders_yet_shows_the_keep_going_sign(self):
        self.client.login(username="rosa", password=PASSWORD)
        response = self.client.get(reverse("checkout:my_orders"))
        self.assertContains(response, "images/sign-no-results.png")
        self.assertNotContains(response, "empty-state.png")

    def test_no_downloads_yet_shows_the_take_a_break_sign(self):
        self.client.login(username="rosa", password=PASSWORD)
        response = self.client.get(reverse("checkout:my_downloads"))
        self.assertContains(response, "images/sign-empty-cart.png")
        self.assertNotContains(response, "empty-state.png")
