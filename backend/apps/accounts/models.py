"""Tenant-isolated provider account metadata.

The actual tokens/cookies are not persisted in these database rows. An opaque
reference points to an encrypted store managed outside Django's public API.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models

from apps.users.models import TenantMembership


class ProviderAccountQuerySet(models.QuerySet):
    def for_owner(self, user):
        return self.filter(owner=user, tenant__memberships__user=user, tenant__memberships__is_active=True)


class ProviderAccount(models.Model):
    class Status(models.TextChoices):
        UNLINKED = "unlinked", "Unlinked"
        REQUIRES_LOGIN = "requires_login", "Requires login"
        CONNECTED = "connected", "Connected"
        EXPIRED = "expired", "Expired"
        DISABLED = "disabled", "Disabled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey("users.Tenant", on_delete=models.CASCADE, related_name="accounts")
    owner = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="provider_accounts")
    provider = models.ForeignKey("providers.Provider", on_delete=models.PROTECT, related_name="accounts")
    connector = models.ForeignKey(
        "providers.Connector", on_delete=models.PROTECT, null=True, blank=True,
        related_name="accounts",
    )
    label = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNLINKED)
    credential_ref = models.CharField(max_length=200, blank=True)
    browser_profile_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProviderAccountQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "provider", "label"], name="iam_account_owner_label_unique"
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"], name="iam_account_tenant_status"),
            models.Index(fields=["owner", "provider"], name="iam_account_owner_provider"),
        ]

    def clean(self):
        super().clean()
        if self.owner_id and self.tenant_id and not TenantMembership.objects.filter(
            tenant_id=self.tenant_id, user_id=self.owner_id, is_active=True
        ).exists():
            raise ValidationError({"owner": "Account owner must be an active tenant member."})
        if self.connector_id and self.provider_id and self.connector.provider_id != self.provider_id:
            raise ValidationError({"connector": "Connector must belong to the selected provider."})

    def save(self, *args, **kwargs):
        self.clean()  # Reject mismatched owner/tenant/connector on ordinary ORM writes.
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.provider_id}:{self.label}"
