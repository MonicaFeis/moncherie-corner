from django.contrib import admin

from .models import Category, Product, ProductImage, ProductOption


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class ProductOptionInline(admin.TabularInline):
    model = ProductOption
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductOptionInline, ProductImageInline]
    list_display = ("name", "category", "product_type", "price", "stock", "is_featured", "is_active")
    list_editable = ("is_featured",)
    list_filter = ("category", "product_type", "is_active")
    search_fields = ("name", "description")
