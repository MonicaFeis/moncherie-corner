from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product

from .cart import Cart, make_key


def read_quantity(request, default=1):
    """Read the quantity from the form. Anything that is not a number counts as the default."""
    try:
        return int(request.POST.get("quantity", default))
    except (TypeError, ValueError):
        return default


def cart_detail(request):
    """Show the bag (US-07, US-08, US-09)."""
    cart = Cart(request)
    context = {"lines": cart.items(), "total": cart.total()}
    return render(request, "cart/cart_detail.html", context)


@require_POST
def add_to_cart(request, product_id):
    """Add a product, and the version the customer chose, to the bag (US-07)."""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = Cart(request)

    if product.is_sold_out:
        messages.error(request, f"售罄 Sorry, {product.name} is sold out.")
        return redirect(product.get_absolute_url())

    option = None
    if product.options.exists():
        option = product.options.filter(pk=request.POST.get("option") or 0).first()
        if option is None:
            messages.error(request, "請選擇 Please choose a version first.")
            return redirect(product.get_absolute_url())

    people = 1
    if product.max_people > 1:
        try:
            people = cart.clean_people(product, int(request.POST.get("people", 1)))
        except (TypeError, ValueError):
            people = 1

    already = cart.data.get(make_key(product, option, people), 0)
    new_quantity = cart.add(product, read_quantity(request), option, people)

    name = f"{product.name} ({option.name})" if option else product.name
    if people > 1:
        name += f", {people} people"
    if new_quantity == already:
        messages.info(request, f"{name} 已經喺購物袋 is already in your bag.")
    else:
        messages.success(request, f"已加入購物袋 Added {name} to your bag.")
    return redirect("cart:detail")


@require_POST
def update_cart(request, key):
    """Change the quantity of a printed item (US-08)."""
    Cart(request).update(key, read_quantity(request))
    messages.success(request, "已更新購物袋 Your bag was updated.")
    return redirect("cart:detail")


@require_POST
def remove_from_cart(request, key):
    """Take a line out of the bag (US-08)."""
    cart = Cart(request)
    line = cart.get_line(key)
    cart.remove(key)
    if line:
        messages.success(request, f"已移除 Removed {line['product'].name} from your bag.")
    return redirect("cart:detail")
