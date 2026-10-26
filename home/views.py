from django.shortcuts import render

from products.models import Category, Product


def index(request):
    """Show the home page with the categories and the newest products."""
    context = {
        "categories": Category.objects.all(),
        "featured": Product.objects.filter(is_active=True)[:4],
    }
    return render(request, "home/index.html", context)
