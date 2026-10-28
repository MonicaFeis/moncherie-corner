"""The owner's pages for orders: see all orders and mark printed ones as shipped (US-36)."""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from notifications.emails import send_order_shipped
from products.views import owner_required

from .forms import ShipOrderForm
from .models import Order


@owner_required
def manage_orders(request):
    """All orders, newest first. "?show=to_ship" shows only orders waiting to be posted."""
    orders = Order.objects.select_related("user").prefetch_related("items")
    show = request.GET.get("show", "all")
    if show == "to_ship":
        orders = [order for order in orders.filter(status=Order.PAID) if order.has_printed_items]
    context = {"orders": orders, "show": show}
    return render(request, "checkout/manage_orders.html", context)


@owner_required
def manage_order(request, order_id):
    """One order. Paid orders with printed items can be marked as shipped."""
    order = get_object_or_404(Order.objects.select_related("user", "shipping_method"), pk=order_id)
    form = ShipOrderForm()

    if request.method == "POST":
        if not order.can_be_shipped:
            messages.error(request, "Only paid orders with printed items can be shipped.")
            return redirect("checkout:manage_order", order_id=order.pk)

        form = ShipOrderForm(request.POST)
        if form.is_valid():
            order.tracking_number = form.cleaned_data["tracking_number"]
            order.status = Order.SHIPPED
            order.save(update_fields=["tracking_number", "status"])
            send_order_shipped(order)
            messages.success(request, f"已寄出 Order #{order.pk} is marked as shipped. The customer has been emailed.")
            return redirect("checkout:manage_order", order_id=order.pk)
        messages.error(request, "Please check the form.")

    return render(request, "checkout/manage_order.html", {"order": order, "form": form})
