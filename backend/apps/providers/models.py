"""Provider registry and versioned connector capability declarations."""

import uuid

from django.db import models


class Provider(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=120)
    homepage_url = models.URLField(blank=True)
    is_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Connector(models.Model):
    class Transport(models.TextChoices):
        OFFICIAL_API = "official_api", "Official API"
        CLI = "cli", "CLI"
        MANUAL_BROWSER = "manual_browser", "Manual browser"
        AUTHORIZED_BROWSER = "authorized_browser", "Authorized browser"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(Provider, on_delete=models.PROTECT, related_name="connectors")
    slug = models.SlugField(max_length=80)
    transport = models.CharField(max_length=24, choices=Transport.choices)
    is_enabled = models.BooleanField(default=False)
    adapter_version = models.CharField(max_length=40, default="0.1")
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["provider", "slug"], name="iam_connector_unique")]

    def __str__(self):
        return f"{self.provider.slug}:{self.slug}"


class Capability(models.Model):
    class Direction(models.TextChoices):
        INPUT = "input", "Input"
        OUTPUT = "output", "Output"

    class Modality(models.TextChoices):
        TEXT = "text", "Text"
        IMAGE = "image", "Image"
        AUDIO = "audio", "Audio"
        VIDEO = "video", "Video"
        DOCUMENT = "document", "Document"
        JSON = "json", "JSON"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE, related_name="capabilities")
    direction = models.CharField(max_length=8, choices=Direction.choices)
    modality = models.CharField(max_length=12, choices=Modality.choices)
    enabled = models.BooleanField(default=False)
    limits = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["connector", "direction", "modality"], name="iam_capability_unique"
            )
        ]
