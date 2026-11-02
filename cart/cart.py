"""The shopping bag (called "cart" in the code).

The cart is kept in the visitor's session (a small storage Django keeps
for each browser), so it works before logging in too.
Only product ids, chosen options and quantities are saved. Prices are ALWAYS
read from the database, so nobody can change a price in their browser.

Each line has a key: "3" for product 3, or "3:7" for product 3 with option 7.
"""
from decimal import Decimal

from products.models import Product, ProductOption

CART_SESSION_KEY = "cart"


def make_key(product, option=None):
    """The key for one line in the cart."""
    return f"{product.pk}:{option.pk}" if option else str(product.pk)


def split_key(key):
    """Turn "3:7" into (3, 7) and "3" into (3, None)."""
    product_id, _, option_id = str(key).partition(":")
    return int(product_id), (int(option_id) if option_id else None)


class Cart:
    def __init__(self, request):
        self.session = request.session
        # The cart looks like this: {"3": 1, "5:2": 1}  (key: quantity)
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

    def add(self, product, quantity=1, option=None):
        """Add a product (and its chosen option). Returns the quantity now in the cart."""
        key = make_key(product, option)
        current = self.data.get(key, 0)
        new_quantity = min(current + quantity, self.max_quantity(product))
        if new_quantity > 0:
            self.data[key] = new_quantity
            self.save()
        return new_quantity

    def get_line(self, key):
        """One line of the cart, or None."""
        for line in self.items():
            if line["key"] == str(key):
                return line
        return None

    def update(self, key, quantity):
        """Set a new quantity. 0 or less removes the line."""
        line = self.get_line(key)
        if line is None or quantity <= 0:
            self.remove(key)
            return 0
        self.data[line["key"]] = min(quantity, line["max_quantity"])
        self.save()
        return self.data[line["key"]]

    def remove(self, key):
        if self.data.pop(str(key), None) is not None:
            self.save()

    def clear(self):
        self.data.clear()
        self.save()

    def items(self):
        """Every line in the cart, with prices from the database.

        Lines whose product (or option) was deleted or hidden are left out.
        """
        keys = []
        for key in self.data:
            try:
                keys.append((key, *split_key(key)))
            except ValueError:
                continue
        products = Product.objects.in_bulk(
            [product_id for _, product_id, _ in keys]
        )
        options = ProductOption.objects.in_bulk(
            [option_id for _, _, option_id in keys if option_id]
        )

        lines = []
        for key, product_id, option_id in keys:
            product = products.get(product_id)
            if product is None or not product.is_active:
                continue
            option = None
            if option_id:
                option = options.get(option_id)
                if option is None or option.product_id != product.pk:
                    continue
            quantity = self.data[key]
            unit_price = product.price + (option.extra_price if option else Decimal("0.00"))
            lines.append({
                "key": key,
                "product": product,
                "option": option,
                "quantity": quantity,
                "max_quantity": self.max_quantity(product),
                "unit_price": unit_price,
                "line_total": unit_price * quantity,
                "needs_shipping": product.product_type == Product.PRINTED
                or bool(option and option.is_printed),
            })
        return lines

    def total(self):
        return sum((line["line_total"] for line in self.items()), Decimal("0.00"))

    def count(self):
        """Number of items, for the bag icon in the navbar."""
        return sum(self.data.values())

    def has_printed_items(self):
        """True if anything needs shipping: printed products or a printed option."""
        return any(line["needs_shipping"] for line in self.items())
