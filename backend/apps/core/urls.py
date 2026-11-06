"""Stage 04 health endpoints. No provider execution yet."""

from django.urls import path

from .views import HealthView, LivenessView, ReadinessView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("live/", LivenessView.as_view(), name="live"),
    path("ready/", ReadinessView.as_view(), name="ready"),
]
