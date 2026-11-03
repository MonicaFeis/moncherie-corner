"""Tests for reviews: only buyers can review, and only their own review can be changed (US-16, US-17)."""
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
        order = Order.objects.create(user=self.buyer, status=Order.PAID, total=Decimal("4.50"))
        order.items.create(product=self.product, product_name=self.product.name,
                           product_type="digital", price=Decimal("4.50"))
        self.page = self.product.get_absolute_url()
        self.add_url = reverse("reviews:add", args=[self.product.slug])

    def login(self, user):
        self.client.login(username=user.username, password=PASSWORD)

    def write_review(self, rating=5, comment="So cute!"):
        return self.client.post(self.add_url, {"rating": rating, "comment": comment})

    def test_buyer_sees_the_review_form(self):
        self.login(self.buyer)
        self.assertContains(self.client.get(self.page), "寫評語 Write a review")

    def test_someone_who_did_not_buy_sees_no_form(self):
        self.login(self.other)
        self.assertNotContains(self.client.get(self.page), "寫評語 Write a review")

    def test_visitor_sees_reviews_but_no_form(self):
        Review.objects.create(product=self.product, user=self.buyer, rating=4, comment="Lovely")
        response = self.client.get(self.page)
        self.assertContains(response, "Lovely")
        self.assertNotContains(response, "寫評語 Write a review")

    def test_buyer_can_add_a_review(self):
        self.login(self.buyer)
        response = self.write_review()
        self.assertRedirects(response, self.page)
        self.assertTrue(Review.objects.filter(user=self.buyer, rating=5).exists())
        self.assertContains(self.client.get(self.page), "So cute!")

    def test_someone_who_did_not_buy_cannot_add_a_review(self):
        self.login(self.other)
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

    def test_average_rating_is_shown(self):
        Review.objects.create(product=self.product, user=self.buyer, rating=4, comment="Nice")
        Review.objects.create(product=self.product, user=self.other, rating=5, comment="Great")
        self.assertContains(self.client.get(self.page), "4.5 / 5")

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
