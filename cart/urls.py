from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_detail, name="detail"),
    path("add/<int:product_id>/", views.add_to_cart, name="add"),
    path("update/<str:key>/", views.update_cart, name="update"),
    path("remove/<str:key>/", views.remove_from_cart, name="remove"),
]
