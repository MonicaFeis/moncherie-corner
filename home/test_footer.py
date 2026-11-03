from django.test import TestCase
from django.urls import reverse


class FooterTests(TestCase):
    def test_footer_logo_links_to_home(self):
        response = self.client.get(reverse("products:list"))
        self.assertContains(response, f'<a href="{reverse("home:index")}" class="d-inline-flex align-items-center gap-2 footer-brand">', html=False)
