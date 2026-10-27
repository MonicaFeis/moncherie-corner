from decimal import ROUND_HALF_UP, Decimal

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from cart.cart import Cart
from products.models import Product

from .forms import CheckoutForm
from .models import Order, OrderItem
from .payments import mark_order_failed, mark_order_paid, read

# Countries we post printed items to
SHIPPING_COUNTRIES = ["DE", "AT", "CH", "FR", "NL", "BE", "LU", "IT", "ES", "GB", "HK"]


def to_cents(amount):
    """Stripe wants prices in cents: €4.50 becomes 450."""
    return int((Decimal(amount) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def build_line_items(order):
    """The list of things Stripe shows on its payment page, using our database prices."""
    line_items = []
    for item in order.items.all():
        line_items.append({
            "price_data": {
                "currency": settings.STRIPE_CURRENCY,
                "unit_amount": to_cents(item.price),
                "product_data": {"name": item.product_name},
            },
            "quantity": item.quantity,
        })
    if order.shipping_cost:
        line_items.append({
            "price_data": {
                "currency": settings.STRIPE_CURRENCY,
                "unit_amount": to_cents(order.shipping_cost),
                "product_data": {"name": f"Shipping: {order.shipping_method.name}"},
            },
            "quantity": 1,
        })
    return line_items


def create_order(user, lines, form):
    """Save a waiting (pending) order with copies of the names and prices."""
    shipping_method = form.cleaned_data.get("shipping_method")
    shipping_cost = shipping_method.price if shipping_method else Decimal("0.00")
    items_total = sum((line["line_total"] for line in lines), Decimal("0.00"))

    order = Order.objects.create(
        user=user,
        shipping_method=shipping_method,
        shipping_cost=shipping_cost,
        notes=form.cleaned_data.get("notes", ""),
        total=items_total + shipping_cost,
    )
    for line in lines:
        product = line["product"]
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_type=product.product_type,
            price=product.price,
            quantity=line["quantity"],
        )
    return order


@login_required
def checkout(request):
    """Check the cart, ask for shipping or portrait notes, then go to Stripe (US-10)."""
    cart = Cart(request)
    lines = cart.items()
    if not lines:
        messages.info(request, "暫時乜都冇 Your bag is empty.")
        return redirect("cart:detail")

    for line in lines:
        if line["product"].is_sold_out:
            messages.error(request, f"售罄 Sorry, {line['product'].name} just sold out.")
            return redirect("cart:detail")

    needs_shipping = cart.has_printed_items()
    needs_notes = any(line["product"].product_type == Product.PORTRAIT for line in lines)
    form_options = {"needs_shipping": needs_shipping, "needs_notes": needs_notes}

    if request.method == "POST":
        form = CheckoutForm(request.POST, **form_options)
        if form.is_valid():
            order = create_order(request.user, lines, form)
            return redirect_to_stripe(request, order, needs_shipping)
        messages.error(request, "Please check the form. 請檢查表格。")
    else:
        form = CheckoutForm(**form_options)

    context = {"lines": lines, "total": cart.total(), "form": form}
    return render(request, "checkout/checkout.html", context)


def redirect_to_stripe(request, order, needs_shipping):
    """Create a Stripe Checkout page for this order and send the customer there."""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    success_url = request.build_absolute_uri(reverse("checkout:success"))
    cancel_url = request.build_absolute_uri(reverse("checkout:cancelled", args=[order.pk]))

    options = {
        "mode": "payment",
        # Our own shop handles the sale, not Stripe Managed Payments
        "managed_payments": {"enabled": False},
        "line_items": build_line_items(order),
        "customer_email": request.user.email,
        "client_reference_id": str(order.pk),
        "metadata": {"order_id": str(order.pk)},
        "success_url": success_url + "?session_id={CHECKOUT_SESSION_ID}",
        "cancel_url": cancel_url,
        "custom_text": {
            "submit": {
                "message": "多謝惠顧！ Thank you for shopping at moncherie corner. "
                "Your files appear in My downloads right after payment."
            }
        },
    }
    if needs_shipping:
        options["shipping_address_collection"] = {"allowed_countries": SHIPPING_COUNTRIES}

    try:
        session = stripe.checkout.Session.create(**options)
    except stripe.StripeError:
        mark_order_failed(order.pk)
        messages.error(request, "付款暫時未能處理 We could not reach the payment service. Please try again.")
        return redirect("cart:detail")

    order.stripe_session_id = session.id
    order.save(update_fields=["stripe_session_id"])
    return redirect(session.url, permanent=False)


@login_required
def success(request):
    """Thank-you page after paying (US-11).

    We ask Stripe directly whether this session was paid, so nobody can
    fake a payment by typing the address.
    """
    session_id = request.GET.get("session_id", "")
    order = get_object_or_404(Order, stripe_session_id=session_id, user=request.user)

    if order.status == Order.PENDING:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.StripeError:
            session = None
        if session is not None and read(session, "payment_status") == "paid":
            mark_order_paid(order.pk, session)
            order.refresh_from_db()

    if order.is_paid:
        Cart(request).clear()
    return render(request, "checkout/success.html", {"order": order})


@login_required
def cancelled(request, order_id):
    """The customer cancelled or the payment failed (US-12)."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    mark_order_failed(order.pk)
    order.refresh_from_db()
    return render(request, "checkout/cancelled.html", {"order": order})


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Stripe calls this address when a payment finishes (US-13)."""
    payload = request.body
    signature = request.headers.get("Stripe-Signature", "")
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.SignatureVerificationError):
        return HttpResponse(status=400)

    session = event["data"]["object"]
    order_id = read(read(session, "metadata", {}), "order_id")
    if not order_id or not Order.objects.filter(pk=order_id).exists():
        return HttpResponse(status=200)

    if event["type"] == "checkout.session.completed" and read(session, "payment_status") == "paid":
        mark_order_paid(order_id, session)
    elif event["type"] == "checkout.session.async_payment_succeeded":
        mark_order_paid(order_id, session)
    elif event["type"] == "checkout.session.async_payment_failed":
        mark_order_failed(order_id)
    elif event["type"] == "checkout.session.expired":
        mark_order_failed(order_id, Order.EXPIRED)

    return HttpResponse(status=200)


@login_required
def my_orders(request):
    """The customer's own orders, newest first (US-14)."""
    orders = request.user.orders.prefetch_related("items")
    return render(request, "checkout/my_orders.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    """One of the customer's own orders (US-31). Other people's orders give a 404."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, "checkout/order_detail.html", {"order": order})


def paid_digital_items(user):
    """Every digital product this customer has paid for, once each."""
    items = OrderItem.objects.filter(
        order__user=user,
        order__status__in=[Order.PAID, Order.SHIPPED],
        product_type=Product.DIGITAL,
        product__isnull=False,
    ).select_related("product", "order")
    seen = set()
    unique_items = []
    for item in items:
        if item.product_id not in seen:
            seen.add(item.product_id)
            unique_items.append(item)
    return unique_items


@login_required
def my_downloads(request):
    """List of files the customer can download (US-15)."""
    return render(request, "checkout/my_downloads.html", {"items": paid_digital_items(request.user)})


@login_required
def download(request, product_id):
    """Send the file, but only to someone who paid for it (US-15)."""
    bought = OrderItem.objects.filter(
        order__user=request.user,
        order__status__in=[Order.PAID, Order.SHIPPED],
        product_id=product_id,
        product_type=Product.DIGITAL,
    ).exists()
    if not bought:
        raise Http404
    product = get_object_or_404(Product, pk=product_id)
    if not product.download_file:
        raise Http404
    file_name = product.download_file.name.split("/")[-1]
    return FileResponse(product.download_file.open("rb"), as_attachment=True, filename=file_name)
