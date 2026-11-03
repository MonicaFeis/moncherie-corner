"""Helpers the product page uses to show reviews."""
from django.db.models import Avg

from checkout.models import Order, OrderItem

from .forms import ReviewForm


def has_bought(user, product):
    """True if this customer paid for this product at least once."""
    if not user.is_authenticated:
        return False
    return OrderItem.objects.filter(
        order__user=user,
        order__status__in=[Order.PAID, Order.SHIPPED],
        product=product,
    ).exists()


def review_context(product, user, form=None):
    """Everything the reviews part of the product page needs."""
    reviews = product.reviews.select_related("user")
    average = reviews.aggregate(Avg("rating"))["rating__avg"]
    own_review = reviews.filter(user=user).first() if user.is_authenticated else None
    can_review = own_review is None and has_bought(user, product)
    return {
        "reviews": reviews,
        "review_count": reviews.count(),
        "average_rating": round(average, 1) if average else None,
        "average_stars": [number <= round(average) for number in range(1, 6)] if average else [],
        "own_review": own_review,
        "review_form": (form or ReviewForm()) if can_review else None,
    }
