from django.urls import path

from . import views

app_name = "checkout"

urlpatterns = [
    path("", views.checkout, name="checkout"),
    path("success/", views.success, name="success"),
    path("cancelled/<int:order_id>/", views.cancelled, name="cancelled"),
    path("webhook/", views.stripe_webhook, name="webhook"),
    path("orders/", views.my_orders, name="my_orders"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("downloads/", views.my_downloads, name="my_downloads"),
    path("downloads/<int:product_id>/", views.download, name="download"),
]
