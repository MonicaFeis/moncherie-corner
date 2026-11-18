"""Tests: the hero poster loads fast (small picture for phones, loaded first)."""
from django.test import TestCase
from django.urls import reverse


class HeroSpeedTests(TestCase):
    def test_hero_has_small_picture_for_phones(self):
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, "hero-poster-800.webp 800w")

    def test_hero_loads_first(self):
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, 'fetchpriority="high"')
