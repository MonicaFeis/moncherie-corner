from django.conf import settings
from django.db import models
from django.urls import reverse

from products.models import Product


class ShippingMethod(models.Model):
    """A way to post printed items, for example "Standard letter post"."""

    name = models.CharField(max_length=80)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    delivery_days = models.PositiveIntegerField(help_text="Usual number of days to arrive.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return f"{self.name} (€{self.price}, about {self.delivery_days} days)"


class Order(models.Model):
    """One purchase by one customer."""

    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SHIPPED = "shipped"
    STATUS_CHOICES = [
        (PENDING, "Waiting for payment"),
        (PAID, "Paid"),
        (CANCELLED, "Payment cancelled"),
        (EXPIRED, "Payment expired"),
        (SHIPPED, "Shipped"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    shipping_method = models.ForeignKey(
        ShippingMethod, on_delete=models.SET_NULL, null=True, blank=True
    )
    shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    shipping_address = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="Notes for a portrait.")
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    stripe_session_id = models.CharField(max_length=255, blank=True)
    tracking_number = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} ({self.get_status_display()})"

    def get_absolute_url(self):
        return reverse("checkout:order_detail", args=[self.pk])

    @property
    def is_paid(self):
        return self.status in (self.PAID, self.SHIPPED)


class OrderItem(models.Model):
    """One line in an order. Name and price are copied, so old orders never change."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=120)
    product_type = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

    @property
    def line_total(self):
        return self.price * self.quantity
