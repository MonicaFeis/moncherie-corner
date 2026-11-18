"""Tests: the hero has one button, "Come on in". The portrait is one product among the others."""
from django.test import TestCase
from django.urls import reverse


class HeroButtonTests(TestCase):
    def test_hero_has_no_commission_a_portrait_button(self):
        response = self.client.get(reverse("home:index"))
        self.assertNotContains(response, "Commission a portrait")
        self.assertContains(response, "Come on in")
