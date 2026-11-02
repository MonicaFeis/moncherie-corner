from django.conf import settings
from django.db import models
from django.urls import reverse

from products.models import Product, download_storage


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

    @property
    def has_digital_items(self):
        """True if there is (or will be) a file to download in this order."""
        return any(item.product_type in ("digital", "portrait") for item in self.items.all())

    @property
    def has_printed_items(self):
        """True if anything in this order needs posting."""
        return any(item.needs_shipping for item in self.items.all())

    @property
    def portrait_items(self):
        """The portraits in this order (they are drawn after payment)."""
        return [item for item in self.items.all() if item.is_portrait]

    @property
    def can_be_shipped(self):
        """Only paid orders with printed items can be marked as shipped."""
        return self.status == self.PAID and self.has_printed_items


class OrderItem(models.Model):
    """One line in an order. Name and price are copied, so old orders never change."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=120)
    product_type = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    option_name = models.CharField(max_length=80, blank=True)
    people = models.PositiveSmallIntegerField(default=1)
    is_printed = models.BooleanField(default=False, help_text="This line is printed and posted.")
    delivered_file = models.FileField(
        upload_to="portraits/", blank=True, storage=download_storage,
        help_text="The finished portrait, uploaded by the owner.",
    )
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.quantity} x {self.display_name}"

    @property
    def display_name(self):
        """Name with the chosen version, for example "Portrait (Digital file)"."""
        extras = [self.option_name] if self.option_name else []
        if self.people > 1:
            extras.append(f"{self.people} people/pets")
        return f"{self.product_name} ({', '.join(extras)})" if extras else self.product_name

    @property
    def line_total(self):
        return self.price * self.quantity

    @property
    def needs_shipping(self):
        return self.is_printed or self.product_type == "printed"

    @property
    def is_portrait(self):
        return self.product_type == "portrait"


class ReferencePhoto(models.Model):
    """A photo the customer sends so the portrait looks like them (US-23)."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reference_photos")
    image = models.ImageField(upload_to="references/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for order #{self.order_id}"
