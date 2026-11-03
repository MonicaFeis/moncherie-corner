"""Tests for reviews: customers review what they received, from My downloads or their order (US-16, US-17)."""
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from checkout.models import Order
from products.models import Category, Product
from reviews.models import Review

PASSWORD = "pass-12345!"


class ReviewTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Stickers", slug="stickers")
        self.product = Product.objects.create(
            category=category, name="Milk Tea Stickers", description="Stickers.", price=Decimal("4.50"),
        )
        self.buyer = User.objects.create_user("rosa", "rosa@example.com", PASSWORD)
        self.other = User.objects.create_user("luca", "luca@example.com", PASSWORD)
        self.order = Order.objects.create(user=self.buyer, status=Order.PAID, total=Decimal("4.50"))
        self.order.items.create(product=self.product, product_name=self.product.name,
                                product_type="digital", price=Decimal("4.50"))
        self.page = self.product.get_absolute_url()
        self.add_url = reverse("reviews:add", args=[self.product.slug])
        self.downloads = reverse("checkout:my_downloads")

    def login(self, user):
        self.client.login(username=user.username, password=PASSWORD)

    def write_review(self, rating=5, comment="So cute!", next_url=""):
        url = self.add_url + (f"?next={next_url}" if next_url else "")
        return self.client.post(url, {"rating": rating, "comment": comment})

    # ---------- where customers find it ----------
    def test_my_downloads_invites_a_review(self):
        self.login(self.buyer)
        response = self.client.get(self.downloads)
        self.assertContains(response, "留個評語 Leave a review")
        self.assertContains(response, self.add_url)

    def test_my_downloads_shows_your_review_after_writing_it(self):
        Review.objects.create(product=self.product, user=self.buyer, rating=4, comment="Lovely")
        self.login(self.buyer)
        response = self.client.get(self.downloads)
        self.assertContains(response, "你嘅評語 Your review")
        self.assertNotContains(response, "留個評語 Leave a review")

    def test_portrait_being_drawn_has_no_review_button(self):
        portrait = Product.objects.create(category=self.product.category, name="Portrait",
                                          description="P.", price=Decimal("30.00"), product_type="portrait")
        order = Order.objects.create(user=self.other, status=Order.PAID, total=Decimal("30.00"))
        order.items.create(product=portrait, product_name="Portrait", product_type="portrait", price=Decimal("30.00"))
        self.login(self.other)
        self.assertNotContains(self.client.get(self.downloads), "留個評語 Leave a review")

    def test_shipped_printed_item_can_be_reviewed_from_the_order(self):
        tote = Product.objects.create(category=self.product.category, name="Tote bag", description="Bag.",
                                      price=Decimal("15.00"), product_type="printed", stock=3)
        order = Order.objects.create(user=self.buyer, status=Order.SHIPPED, total=Decimal("15.00"))
        order.items.create(product=tote, product_name="Tote bag", product_type="printed", price=Decimal("15.00"))
        self.login(self.buyer)
        response = self.client.get(reverse("checkout:order_detail", args=[order.pk]))
        self.assertContains(response, reverse("reviews:add", args=[tote.slug]))

    def test_review_page_has_a_friendly_question(self):
        self.login(self.buyer)
        response = self.client.get(self.add_url)
        self.assertContains(response, "留個評語 Leave a review")
        self.assertContains(response, "Did your stickers find a new home?")

    # ---------- writing a review ----------
    def test_buyer_can_add_a_review_and_go_back_to_my_downloads(self):
        self.login(self.buyer)
        response = self.write_review(next_url=self.downloads)
        self.assertRedirects(response, self.downloads)
        self.assertTrue(Review.objects.filter(user=self.buyer, rating=5).exists())

    def test_review_shows_on_the_product_page(self):
        Review.objects.create(product=self.product, user=self.buyer, rating=4, comment="Lovely")
        response = self.client.get(self.page)
        self.assertContains(response, "Lovely")
        self.assertContains(response, "4.0 / 5")

    def test_someone_who_did_not_buy_cannot_review(self):
        self.login(self.other)
        self.assertRedirects(self.client.get(self.add_url), self.page)
        self.write_review()
        self.assertFalse(Review.objects.exists())

    def test_only_one_review_per_product(self):
        self.login(self.buyer)
        self.write_review()
        self.write_review(rating=1, comment="Second try")
        self.assertEqual(Review.objects.count(), 1)

    def test_rating_must_be_1_to_5(self):
        self.login(self.buyer)
        self.write_review(rating=9)
        self.assertFalse(Review.objects.exists())

    def test_next_must_be_on_this_site(self):
        self.login(self.buyer)
        response = self.write_review(next_url="https://example.com/")
        self.assertRedirects(response, self.page, fetch_redirect_response=False)

    def test_average_rating_is_shown(self):
        Review.objects.create(product=self.product, user=self.buyer, rating=4, comment="Nice")
        Review.objects.create(product=self.product, user=self.other, rating=5, comment="Great")
        self.assertContains(self.client.get(self.page), "4.5 / 5")

    # ---------- changing or deleting ----------
    def test_owner_of_the_review_can_edit_it(self):
        review = Review.objects.create(product=self.product, user=self.buyer, rating=3, comment="OK")
        self.login(self.buyer)
        self.client.post(reverse("reviews:edit", args=[review.pk]), {"rating": 5, "comment": "Even better"})
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Even better")

    def test_other_people_cannot_edit_or_delete_it(self):
        review = Review.objects.create(product=self.product, user=self.buyer, rating=3, comment="OK")
        self.login(self.other)
        self.assertEqual(self.client.get(reverse("reviews:edit", args=[review.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("reviews:delete", args=[review.pk])).status_code, 404)
        self.assertTrue(Review.objects.filter(pk=review.pk).exists())

    def test_delete_asks_first_then_deletes(self):
        review = Review.objects.create(product=self.product, user=self.buyer, rating=3, comment="OK")
        self.login(self.buyer)
        confirm = self.client.get(reverse("reviews:delete", args=[review.pk]))
        self.assertContains(confirm, "Delete your review?")
        self.assertTrue(Review.objects.filter(pk=review.pk).exists())
        self.client.post(reverse("reviews:delete", args=[review.pk]))
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())
