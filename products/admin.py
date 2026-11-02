from django.contrib import admin

from .models import Category, Product, ProductOption


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class ProductOptionInline(admin.TabularInline):
    model = ProductOption
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductOptionInline]
    list_display = ("name", "category", "product_type", "price", "stock", "is_active")
    list_filter = ("category", "product_type", "is_active")
    search_fields = ("name", "description")
