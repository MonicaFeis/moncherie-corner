from django.contrib import admin

from .models import ReferencePhoto, Order, OrderItem, ShippingMethod


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "option_name", "people", "product_type", "is_printed", "price", "quantity")


class ReferencePhotoInline(admin.TabularInline):
    model = ReferencePhoto
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "status", "total", "created_at")
    list_filter = ("status",)
    inlines = [OrderItemInline, ReferencePhotoInline]


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "delivery_days", "is_active")
