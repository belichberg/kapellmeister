from django.urls import path
from .views import health, ContainerView


urlpatterns = [
    path("health/", health),
    path("<slug:project_slug>/<slug:channel_slug>/", ContainerView.as_view()),
]
