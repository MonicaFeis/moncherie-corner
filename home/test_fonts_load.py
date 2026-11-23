"""Tests: Google Fonts load without blocking the page (faster on phones)."""
from django.test import TestCase
from django.urls import reverse


class FontLoadingTests(TestCase):
    def test_google_fonts_do_not_block_the_page(self):
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, 'media="print" onload="this.media=\'all\'"')

    def test_fonts_still_load_without_javascript(self):
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, "<noscript>")
