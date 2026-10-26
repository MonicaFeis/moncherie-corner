from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="list"),
    path("manage/", views.manage_products, name="manage"),
    path("manage/add/", views.add_product, name="add"),
    path("manage/<int:pk>/edit/", views.edit_product, name="edit"),
    path("manage/<int:pk>/delete/", views.delete_product, name="delete"),
    path("<slug:slug>/", views.product_detail, name="detail"),
]
