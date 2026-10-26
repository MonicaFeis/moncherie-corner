from .cart import Cart


def cart(request):
    """Make the cart count available on every page (for the navbar bag)."""
    return {"cart_count": Cart(request).count()}
