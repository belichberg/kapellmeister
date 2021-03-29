from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

from kapellmeister import settings
from management.views import index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index),
    path("api/v1/", include("management.urls")),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
