from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

from .emails import send_welcome_email


class WelcomeEmailTests(TestCase):
    """US-39: new customers get a welcome email."""

    def setUp(self):
        self.user = User.objects.create_user("cherry", "cherry@example.com", "pass-12345!")

    def test_welcome_email_goes_to_the_user(self):
        sent = send_welcome_email(self.user)
        self.assertTrue(sent)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ["cherry@example.com"])
        self.assertIn("Welcome", email.subject)
        self.assertIn("cherry", email.body)

    def test_welcome_email_has_an_html_version(self):
        send_welcome_email(self.user)
        html, mime_type = mail.outbox[0].alternatives[0]
        self.assertEqual(mime_type, "text/html")
        self.assertIn("moncherie corner", html)

    def test_mail_server_problem_does_not_crash(self):
        with patch("notifications.emails.EmailMultiAlternatives.send", side_effect=OSError):
            sent = send_welcome_email(self.user)
        self.assertFalse(sent)
