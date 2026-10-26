"""Main list of web addresses. Each app has its own urls.py file."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("home.urls")),
]
