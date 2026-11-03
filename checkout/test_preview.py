"""Tests: a finished portrait shows its own picture in My downloads (US-24)."""
from decimal import Decimal

from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils import timezone

from .models import Order
from .tests import PASSWORD, CheckoutTestCase


class PortraitPreviewTests(CheckoutTestCase):
    def setUp(self):
        super().setUp()
        order = Order.objects.create(user=self.user, status=Order.PAID, total=Decimal("30.00"))
        self.item = order.items.create(product_name="Portrait", product_type="portrait", price=Decimal("30.00"))
        self.item.delivered_file.save("rosa.png", ContentFile(b"png-data"))
        self.item.delivered_at = timezone.now()
        self.item.save()
        self.preview_url = reverse("checkout:preview_portrait", args=[self.item.pk])

    def test_ready_card_shows_the_finished_portrait(self):
        response = self.client.get(reverse("checkout:my_downloads"))
        self.assertContains(response, f'src="{self.preview_url}"')

    def test_preview_shows_the_picture_in_the_page(self):
        response = self.client.get(self.preview_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("attachment", response.get("Content-Disposition", ""))

    def test_other_customer_cannot_see_the_preview(self):
        self.client.login(username="other", password=PASSWORD)
        self.assertEqual(self.client.get(self.preview_url).status_code, 404)

    def test_pdf_portrait_shows_the_product_picture_instead(self):
        self.item.delivered_file.save("rosa.pdf", ContentFile(b"pdf"))
        response = self.client.get(reverse("checkout:my_downloads"))
        self.assertNotContains(response, f'src="{self.preview_url}"')
