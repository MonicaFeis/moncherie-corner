from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    """The home page and the 404 page."""

    def test_home_page_loads(self):
        response = self.client.get(reverse("home:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/index.html")
        self.assertContains(response, "Welcome to the corner.")

    def test_home_page_has_navbar_and_footer(self):
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, "<nav", html=False)
        self.assertContains(response, "<footer", html=False)

    def test_missing_page_shows_friendly_404(self):
        response = self.client.get("/this-page-does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")


