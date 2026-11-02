"""The shopping bag (called "cart" in the code).

The cart is kept in the visitor's session (a small storage Django keeps
for each browser), so it works before logging in too.
Only product ids, chosen options and quantities are saved. Prices are ALWAYS
read from the database, so nobody can change a price in their browser.

Each line has a key: "3" for product 3, "3:7" for product 3 with option 7,
and "3:7:p2" when the customer chose a portrait with 2 people.
"""
from decimal import Decimal

from products.models import Product, ProductOption

CART_SESSION_KEY = "cart"


def make_key(product, option=None, people=1):
    """The key for one line in the cart."""
    key = str(product.pk)
    if option:
        key += f":{option.pk}"
    if people > 1:
        key += f":p{people}"
    return key


def split_key(key):
    """Turn "3:7:p2" into (3, 7, 2) and "3" into (3, None, 1)."""
    first, *rest = str(key).split(":")
    option_id, people = None, 1
    for part in rest:
        if part.startswith("p"):
            people = int(part[1:])
        else:
            option_id = int(part)
    return int(first), option_id, people


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

    def add(self, product, quantity=1, option=None, people=1):
        """Add a product (and its chosen option). Returns the quantity now in the cart."""
        key = make_key(product, option, self.clean_people(product, people))
        current = self.data.get(key, 0)
        new_quantity = min(current + quantity, self.max_quantity(product))
        if new_quantity > 0:
            self.data[key] = new_quantity
            self.save()
        return new_quantity

    def clean_people(self, product, people):
        """Keep the number of people between 1 and the product's maximum."""
        return max(1, min(people, product.max_people))

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
            [product_id for _, product_id, _, _ in keys]
        )
        options = ProductOption.objects.in_bulk(
            [option_id for _, _, option_id, _ in keys if option_id]
        )

        lines = []
        for key, product_id, option_id, people in keys:
            product = products.get(product_id)
            if product is None or not product.is_active:
                continue
            option = None
            if option_id:
                option = options.get(option_id)
                if option is None or option.product_id != product.pk:
                    continue
            quantity = self.data[key]
            people = self.clean_people(product, people)
            unit_price = product.price + (option.extra_price if option else Decimal("0.00"))
            unit_price += product.extra_person_price * (people - 1)
            lines.append({
                "key": key,
                "product": product,
                "option": option,
                "people": people,
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
