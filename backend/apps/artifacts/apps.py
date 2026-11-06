"""App namespace reserved for Stage 06+ models and API routes."""

from django.apps import AppConfig


class ArtifactsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.artifacts"
