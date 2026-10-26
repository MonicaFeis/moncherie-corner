"""The shopping cart.

The cart is kept in the visitor's session (a small storage Django keeps
for each browser), so it works before logging in too.
Only product ids and quantities are saved. Prices are ALWAYS read
from the database, so nobody can change a price in their browser.
"""
from decimal import Decimal

from products.models import Product

CART_SESSION_KEY = "cart"


class Cart:
    def __init__(self, request):
        self.session = request.session
        # The cart looks like this: {"3": 1, "7": 2}  (product id: quantity)
        self.data = self.session.setdefault(CART_SESSION_KEY, {})

    def save(self):
        """Tell Django the session changed, so it is stored."""
        self.session.modified = True

    def max_quantity(self, product):
        """How many of this product one order may have.

        Digital files and portraits: only 1 (you never need two copies).
        Printed items: as many as are in stock.
        """
        if product.product_type == Product.PRINTED:
            return product.stock
        return 1

    def add(self, product, quantity=1):
        """Add a product. Returns the quantity now in the cart."""
        current = self.data.get(str(product.pk), 0)
        new_quantity = min(current + quantity, self.max_quantity(product))
        if new_quantity > 0:
            self.data[str(product.pk)] = new_quantity
            self.save()
        return new_quantity

    def update(self, product, quantity):
        """Set a new quantity. 0 or less removes the product."""
        if quantity <= 0:
            self.remove(product.pk)
            return 0
        self.data[str(product.pk)] = min(quantity, self.max_quantity(product))
        self.save()
        return self.data[str(product.pk)]

    def remove(self, product_id):
        if self.data.pop(str(product_id), None) is not None:
            self.save()

    def clear(self):
        self.data.clear()
        self.save()

    def items(self):
        """Every line in the cart, with the product and its price from the database.

        Products that were deleted or hidden since they were added are left out.
        """
        products = Product.objects.filter(pk__in=self.data.keys(), is_active=True)
        lines = []
        for product in products:
            quantity = self.data[str(product.pk)]
            lines.append({
                "product": product,
                "quantity": quantity,
                "max_quantity": self.max_quantity(product),
                "line_total": product.price * quantity,
            })
        return lines

    def total(self):
        return sum((line["line_total"] for line in self.items()), Decimal("0.00"))

    def count(self):
        """Number of items, for the bag icon in the navbar."""
        return sum(self.data.values())

    def has_printed_items(self):
        """True if anything needs shipping (used later in checkout)."""
        return any(
            line["product"].product_type == Product.PRINTED for line in self.items()
        )
