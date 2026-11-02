"""The owner's pages for orders: see all orders, mark printed ones as shipped (US-36)
and upload finished portraits (US-24)."""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from notifications.emails import send_order_shipped, send_portrait_ready
from products.views import owner_required

from .forms import DeliverPortraitForm, ShipOrderForm
from .models import Order


@owner_required
def manage_orders(request):
    """All orders, newest first. "?show=to_ship" shows only orders waiting to be posted,
    "?show=to_draw" only paid portraits that are not delivered yet."""
    orders = Order.objects.select_related("user").prefetch_related("items")
    show = request.GET.get("show", "all")
    if show == "to_ship":
        orders = [order for order in orders.filter(status=Order.PAID) if order.has_printed_items]
    elif show == "to_draw":
        orders = [
            order for order in orders.filter(status__in=[Order.PAID, Order.SHIPPED])
            if any(not item.delivered_file for item in order.portrait_items)
        ]
    context = {"orders": orders, "show": show}
    return render(request, "checkout/manage_orders.html", context)


def ship_order(request, order):
    """Save the tracking number and email the customer."""
    if not order.can_be_shipped:
        messages.error(request, "Only paid orders with printed items can be shipped.")
        return None
    form = ShipOrderForm(request.POST)
    if form.is_valid():
        order.tracking_number = form.cleaned_data["tracking_number"]
        order.status = Order.SHIPPED
        order.save(update_fields=["tracking_number", "status"])
        send_order_shipped(order)
        messages.success(request, f"已寄出 Order #{order.pk} is marked as shipped. The customer has been emailed.")
        return None
    messages.error(request, "Please check the form.")
    return form


def deliver_portrait(request, order):
    """Upload the finished portrait for one line and email the customer."""
    item = order.items.filter(pk=request.POST.get("item_id") or 0, product_type="portrait").first()
    if item is None or not order.is_paid:
        messages.error(request, "Portraits can only be delivered for paid orders.")
        return None, None
    form = DeliverPortraitForm(request.POST, request.FILES)
    if form.is_valid():
        item.delivered_file = form.cleaned_data["portrait_file"]
        item.delivered_at = timezone.now()
        item.save(update_fields=["delivered_file", "delivered_at"])
        send_portrait_ready(item)
        messages.success(request, f"已交付 The portrait for order #{order.pk} is ready. The customer has been emailed.")
        return None, None
    messages.error(request, "Please check the portrait file.")
    return item.pk, form


@owner_required
def manage_order(request, order_id):
    """One order. The owner can mark it shipped or upload finished portraits."""
    order = get_object_or_404(Order.objects.select_related("user", "shipping_method"), pk=order_id)
    ship_form = ShipOrderForm()
    portrait_errors = {}

    if request.method == "POST":
        if request.POST.get("action") == "deliver":
            item_id, form = deliver_portrait(request, order)
            if form is None:
                return redirect("checkout:manage_order", order_id=order.pk)
            portrait_errors[item_id] = form
        else:
            form = ship_order(request, order)
            if form is None:
                return redirect("checkout:manage_order", order_id=order.pk)
            ship_form = form

    portrait_rows = [
        {"item": item, "form": portrait_errors.get(item.pk) or DeliverPortraitForm(auto_id=f"id_%s_{item.pk}")}
        for item in order.portrait_items
    ]
    context = {"order": order, "form": ship_form, "portrait_rows": portrait_rows}
    return render(request, "checkout/manage_order.html", context)
