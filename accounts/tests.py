from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

PASSWORD = "S3cure-pass-42"


class RegisterTests(TestCase):
    """US-01: a visitor can create an account."""

    def setUp(self):
        self.url = reverse("accounts:register")
        self.valid_data = {
            "username": "cherry",
            "email": "cherry@example.com",
            "password1": PASSWORD,
            "password2": PASSWORD,
        }

    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, reverse("home:index"))
        self.assertTrue(User.objects.filter(username="cherry").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_register_sends_welcome_email(self):
        self.client.post(self.url, self.valid_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["cherry@example.com"])

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user("other", "cherry@example.com", PASSWORD)
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="cherry").exists())
        self.assertContains(response, "already exists")

    def test_weak_password_is_rejected(self):
        data = {**self.valid_data, "password1": "1234", "password2": "1234"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="cherry").exists())


class LoginLogoutTests(TestCase):
    """US-02 and US-03: log in, log out, and pages only for visitors."""

    def setUp(self):
        User.objects.create_user("cherry", "cherry@example.com", PASSWORD)

    def test_login_with_correct_details(self):
        response = self.client.post(
            reverse("accounts:login"), {"username": "cherry", "password": PASSWORD}
        )
        self.assertRedirects(response, reverse("home:index"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_with_wrong_password_fails(self):
        response = self.client.post(
            reverse("accounts:login"), {"username": "cherry", "password": "wrong"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logged_in_user_is_sent_away_from_login(self):
        self.client.login(username="cherry", password=PASSWORD)
        response = self.client.get(reverse("accounts:login"))
        self.assertRedirects(response, reverse("home:index"))

    def test_logged_in_user_is_sent_away_from_register(self):
        self.client.login(username="cherry", password=PASSWORD)
        response = self.client.get(reverse("accounts:register"))
        self.assertRedirects(response, reverse("home:index"))

    def test_logout_ends_the_session(self):
        self.client.login(username="cherry", password=PASSWORD)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("home:index"))
        self.assertNotIn("_auth_user_id", self.client.session)
