"""Private uploaded and generated files. Never expose storage_key as a public URL."""

import uuid

from django.core.exceptions import ValidationError
from django.db import models


class ArtifactQuerySet(models.QuerySet):
    def for_owner(self, user):
        return self.filter(owner=user, tenant__memberships__user=user, tenant__memberships__is_active=True)


class Artifact(models.Model):
    class Direction(models.TextChoices):
        INPUT = "input", "Input attachment"
        OUTPUT = "output", "Generated output"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey("users.Tenant", on_delete=models.CASCADE, related_name="artifacts")
    owner = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="artifacts")
    job = models.ForeignKey(
        "jobs.Job", on_delete=models.SET_NULL, null=True, blank=True, related_name="artifacts"
    )
    message = models.ForeignKey(
        "chats.Message", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="artifacts",
    )
    direction = models.CharField(max_length=8, choices=Direction.choices)
    storage_key = models.CharField(max_length=300, unique=True)
    original_filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=180)
    byte_size = models.PositiveBigIntegerField(default=0)
    sha256 = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    objects = ArtifactQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=["owner", "-created_at"], name="iam_art_owner_created"),
            models.Index(fields=["tenant", "sha256"], name="iam_art_tenant_sha"),
            models.Index(fields=["job", "direction"], name="iam_art_job_direction"),
        ]

    def clean(self):
        super().clean()
        if self.job_id and (
            self.job.owner_id != self.owner_id or self.job.tenant_id != self.tenant_id
        ):
            raise ValidationError({"job": "Artifact job belongs to another owner/tenant."})
        if self.message_id and (
            self.message.chat.owner_id != self.owner_id
            or self.message.chat.tenant_id != self.tenant_id
        ):
            raise ValidationError({"message": "Artifact message belongs to another owner/tenant."})

    def __str__(self):
        return f"Artifact {self.pk}"
