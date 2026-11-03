"""Tests: the Chinese shop name 車厘小角 shows next to moncherie corner."""
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from notifications.emails import send_welcome_email


class ShopNameTests(TestCase):
    def test_header_and_footer_show_the_chinese_name(self):
        response = self.client.get(reverse("home:index"))
        self.assertGreaterEqual(response.content.decode().count("車厘小角"), 2)
        self.assertNotContains(response, "轉角小店")

    def test_page_title_has_the_chinese_name(self):
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, "<title>moncherie corner 車厘小角</title>", html=False)

    def test_emails_show_the_chinese_name(self):
        user = User.objects.create_user("rosa", "rosa@example.com", "pass-12345!")
        mail.outbox = []
        send_welcome_email(user)
        html = mail.outbox[0].alternatives[0][0]
        self.assertIn("車厘小角", html)
        self.assertNotIn("轉角小店", html)
