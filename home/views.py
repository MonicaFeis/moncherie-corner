from django.shortcuts import render

from products.models import Category, Product
from reviews.models import Review


def index(request):
    """Show the home page with the categories and the newest products."""
    context = {
        "categories": Category.objects.all(),
        "featured": Product.objects.filter(is_active=True)[:4],
        # The "Commission a portrait" button opens this product's order page
        "portrait_product": Product.objects.filter(
            is_active=True, product_type=Product.PORTRAIT
        ).first(),
        # The 3 newest reviews with 4 or 5 stars, for "What customers say"
        "happy_reviews": Review.objects.filter(rating__gte=4, product__is_active=True)
        .select_related("user", "product")[:3],
    }
    return render(request, "home/index.html", context)
