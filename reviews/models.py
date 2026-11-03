from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from products.models import Product


class Review(models.Model):
    """A customer's rating and comment for a product they bought (US-16)."""

    RATING_CHOICES = [
        (5, "5 · 好鍾意 Love it"),
        (4, "4 · 好好 Really good"),
        (3, "3 · 幾好 Good"),
        (2, "2 · 麻麻 Not great"),
        (1, "1 · 唔鍾意 Did not like it"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # One review per customer per product
            models.UniqueConstraint(fields=["product", "user"], name="one_review_per_product"),
        ]

    def __str__(self):
        return f"{self.user} on {self.product}: {self.rating}/5"

    @property
    def star_list(self):
        """[True, True, True, False, False] for 3 stars, so the page can draw them."""
        return [number <= self.rating for number in range(1, 6)]
