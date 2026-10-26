"""Everything that changes an order after Stripe tells us what happened.

Both the success page and the Stripe webhook call these functions.
They are safe to call twice: an order is only marked paid once,
so stock goes down once and only one email is sent.
"""
from django.db import transaction
from django.db.models import F

from notifications.emails import send_order_confirmation, send_payment_failed
from products.models import Product

from .models import Order


def read(stripe_object, key, default=None):
    """Read one value from a Stripe object or a normal dictionary."""
    try:
        value = stripe_object[key]
    except (KeyError, TypeError, AttributeError):
        return default
    return default if value is None else value


def format_address(session):
    """Turn the address Stripe collected into a few lines of text."""
    details = read(read(session, "collected_information"), "shipping_details") or read(
        session, "shipping_details"
    )
    if not details:
        return ""
    address = read(details, "address", {})
    parts = [
        read(details, "name", ""),
        read(address, "line1", ""),
        read(address, "line2", ""),
        f"{read(address, 'postal_code', '')} {read(address, 'city', '')}".strip(),
        read(address, "country", ""),
    ]
    return "\n".join(part for part in parts if part)


def mark_order_paid(order_id, session=None):
    """Mark the order paid, lower the stock and send the confirmation email.

    Returns True the first time, False if the order was already handled.
    """
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order_id)
        if order.status != Order.PENDING:
            return False

        order.status = Order.PAID
        if session is not None:
            order.shipping_address = format_address(session) or order.shipping_address
        order.save()

        for item in order.items.filter(product_type=Product.PRINTED, product__isnull=False):
            Product.objects.filter(pk=item.product_id, stock__gte=item.quantity).update(
                stock=F("stock") - item.quantity
            )

    send_order_confirmation(order)
    return True


def mark_order_failed(order_id, status=Order.CANCELLED):
    """Mark a waiting order as cancelled or expired and tell the customer."""
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order_id)
        if order.status != Order.PENDING:
            return False
        order.status = status
        order.save()

    send_payment_failed(order)
    return True
