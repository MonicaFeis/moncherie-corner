from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Category, Product


def owner_required(view):
    """Only the shop owner (a staff user) may use these pages (US-21).

    Visitors are sent to log in. Logged-in customers get "403 Forbidden".
    """
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


def product_list(request):
    """Show all active products, or only one category (US-04)."""
    products = Product.objects.filter(is_active=True).select_related("category")
    current_category = None

    category_slug = request.GET.get("category")
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    context = {
        "products": products,
        "categories": Category.objects.all(),
        "current_category": current_category,
    }
    return render(request, "products/product_list.html", context)


def product_detail(request, slug):
    """Show one product (US-05). Hidden products give a 404."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "products/product_detail.html", {"product": product})


@owner_required
def manage_products(request):
    """The owner's list of all products, including hidden ones."""
    products = Product.objects.select_related("category")
    return render(request, "products/manage_list.html", {"products": products})


@owner_required
def add_product(request):
    """Add a new product (US-18)."""
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Added {product.name}.")
            return redirect("products:manage")
        messages.error(request, "Please check the form for errors.")
    else:
        form = ProductForm()
    return render(request, "products/product_form.html", {"form": form, "title": "Add a product"})


@owner_required
def edit_product(request, pk):
    """Change an existing product (US-19)."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Saved changes to {product.name}.")
            return redirect("products:manage")
        messages.error(request, "Please check the form for errors.")
    else:
        form = ProductForm(instance=product)
    context = {"form": form, "title": f"Edit {product.name}", "product": product}
    return render(request, "products/product_form.html", context)


@owner_required
def delete_product(request, pk):
    """Ask first, then delete the product (US-20)."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        name = product.name
        product.delete()
        messages.success(request, f"Deleted {name}.")
        return redirect("products:manage")
    return render(request, "products/product_confirm_delete.html", {"product": product})
