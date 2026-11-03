"""Helpers for reviews: who may review, and what the pages need."""
from django.db.models import Avg

from checkout.models import Order, OrderItem

from .models import Review

# A friendly question for each kind of product
QUESTIONS = {
    "digital": "貼咗未？ Did your stickers find a new home? Tell me how you are using them.",
    "portrait": "你鍾唔鍾意？ Did your portrait make you smile? I would love to hear.",
    "printed": "收到未？ Has your parcel arrived safely? Tell me what you think.",
}


def question_for(product_type):
    return QUESTIONS.get(product_type, QUESTIONS["digital"])


def has_bought(user, product):
    """True if this customer paid for this product at least once."""
    if not user.is_authenticated:
        return False
    return OrderItem.objects.filter(
        order__user=user,
        order__status__in=[Order.PAID, Order.SHIPPED],
        product=product,
    ).exists()


def attach_reviews(user, items):
    """Give each order line .my_review (the customer's review, or None) and .review_question."""
    reviews = {review.product_id: review for review in Review.objects.filter(user=user)}
    for item in items:
        item.my_review = reviews.get(item.product_id)
        item.review_question = question_for(item.product_type)
    return items


def review_context(product, user):
    """Everything the reviews part of the product page needs."""
    reviews = product.reviews.select_related("user")
    average = reviews.aggregate(Avg("rating"))["rating__avg"]
    own_review = reviews.filter(user=user).first() if user.is_authenticated else None
    return {
        "reviews": reviews,
        "review_count": reviews.count(),
        "average_rating": round(average, 1) if average else None,
        "average_stars": [number <= round(average) for number in range(1, 6)] if average else [],
        "own_review": own_review,
        "can_review": own_review is None and has_bought(user, product),
    }
