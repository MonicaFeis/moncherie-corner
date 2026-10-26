from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product

from .cart import Cart


def read_quantity(request, default=1):
    """Read the quantity from the form. Anything that is not a number counts as the default."""
    try:
        return int(request.POST.get("quantity", default))
    except (TypeError, ValueError):
        return default


def cart_detail(request):
    """Show the cart (US-07, US-08, US-09)."""
    cart = Cart(request)
    context = {"lines": cart.items(), "total": cart.total()}
    return render(request, "cart/cart_detail.html", context)


@require_POST
def add_to_cart(request, product_id):
    """Add a product to the cart (US-07)."""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = Cart(request)

    if product.is_sold_out:
        messages.error(request, f"售罄 Sorry, {product.name} is sold out.")
        return redirect(product.get_absolute_url())

    already = request.session.get("cart", {}).get(str(product.pk), 0)
    new_quantity = cart.add(product, read_quantity(request))

    if new_quantity == already:
        messages.info(request, f"{product.name} 已經喺購物車 is already in your cart.")
    else:
        messages.success(request, f"已加入購物車 Added {product.name} to your cart.")
    return redirect("cart:detail")


@require_POST
def update_cart(request, product_id):
    """Change the quantity of a printed item (US-08)."""
    product = get_object_or_404(Product, pk=product_id)
    Cart(request).update(product, read_quantity(request))
    messages.success(request, "已更新購物車 Your cart was updated.")
    return redirect("cart:detail")


@require_POST
def remove_from_cart(request, product_id):
    """Take a product out of the cart (US-08)."""
    product = get_object_or_404(Product, pk=product_id)
    Cart(request).remove(product.pk)
    messages.success(request, f"已移除 Removed {product.name} from your cart.")
    return redirect("cart:detail")
