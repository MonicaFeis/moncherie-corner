"""Tests: pictures from Cloudinary are sent smaller and in a modern format (faster pages)."""
from django.template import Context, Template
from django.test import TestCase
from django.urls import reverse

from products.templatetags.shop_images import sized

CLOUD = "https://res.cloudinary.com/demo/image/upload/v1/media/products/stickers.jpg"


class ImageSizeTests(TestCase):
    def test_cloudinary_picture_gets_a_width(self):
        self.assertEqual(
            sized(CLOUD, 600),
            "https://res.cloudinary.com/demo/image/upload/f_auto,q_auto,w_600/v1/media/products/stickers.jpg",
        )

    def test_other_pictures_stay_the_same(self):
        self.assertEqual(sized("/media/products/stickers.jpg", 600), "/media/products/stickers.jpg")

    def test_filter_works_in_a_template(self):
        html = Template("{% load shop_images %}{{ url|sized:400 }}").render(Context({"url": CLOUD}))
        self.assertIn("w_400", html)

    def test_font_awesome_does_not_block_the_page(self):
        response = self.client.get(reverse("home:index"))
        self.assertContains(response, 'kit.fontawesome.com/ad8754aeee.js" crossorigin="anonymous" defer')
