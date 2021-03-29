from django.contrib import admin
from django.urls import path, include
from management.views import index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index),
    path("api/v1/", include("management.urls")),
]
