"""API token metadata and scoped allowlists; never persist plaintext secrets."""

import hashlib
import hmac
import secrets
import uuid

from django.db import models
from django.utils import timezone


def digest_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


class ApiTokenManager(models.Manager):
    def for_owner(self, user):
        return self.get_queryset().filter(owner=user, tenant__memberships__user=user, tenant__memberships__is_active=True)

    def issue(self, *, tenant, owner, label, expires_at=None):
        """Return (persisted metadata, plaintext once). Caller must check tenant authorization."""
        if not tenant.memberships.filter(user=owner, is_active=True).exists():
            raise ValueError("Token owner must have an active tenant membership")
        raw = "aim_" + secrets.token_urlsafe(40)
        instance = self.create(
            tenant=tenant,
            owner=owner,
            label=label,
            display_prefix=raw[:16],
            token_digest=digest_token(raw),
            expires_at=expires_at,
        )
        return instance, raw

    def authenticate(self, raw_token):
        """Verify digest and validity. Authorization scopes are checked separately."""
        if not isinstance(raw_token, str) or not raw_token.startswith("aim_"):
            return None
        digest = digest_token(raw_token)
        candidate = self.get_queryset().filter(token_digest=digest).first()
        if candidate is None or candidate.revoked_at is not None:
            return None
        if candidate.expires_at and candidate.expires_at <= timezone.now():
            return None
        if not hmac.compare_digest(candidate.token_digest, digest):
            return None
        return candidate


class ApiToken(models.Model):
    class AccessMode(models.TextChoices):
        SELECTED = "selected", "Selected accounts"
        PROVIDER = "provider", "All owned accounts on allowed provider"
        SINGLE = "single", "Single account"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey("users.Tenant", on_delete=models.CASCADE, related_name="api_tokens")
    owner = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="api_tokens")
    label = models.CharField(max_length=100)
    display_prefix = models.CharField(max_length=16, unique=True, editable=False)
    token_digest = models.CharField(max_length=64, unique=True, editable=False)
    access_mode = models.CharField(
        max_length=12, choices=AccessMode.choices, default=AccessMode.SELECTED
    )
    allowed_providers = models.ManyToManyField("providers.Provider", blank=True)
    allowed_accounts = models.ManyToManyField("accounts.ProviderAccount", blank=True)
    scopes = models.JSONField(default=list, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ApiTokenManager()

    class Meta:
        indexes = [
            models.Index(fields=["owner", "revoked_at"], name="iam_token_owner_revoked"),
            models.Index(fields=["tenant", "expires_at"], name="iam_token_tenant_expiry"),
        ]

    def __str__(self):
        return f"API Token {self.display_prefix}…"

    def is_valid(self):
        return self.revoked_at is None and (
            self.expires_at is None or self.expires_at > timezone.now()
        )

    def allows_account(self, account):
        """Fail closed for cross-user/tenant; evaluate explicit mode and allowlist."""
        if not self.is_valid() or account.owner_id != self.owner_id:
            return False
        if account.tenant_id != self.tenant_id or account.status == "disabled":
            return False
        if self.access_mode == self.AccessMode.PROVIDER:
            return self.allowed_providers.filter(pk=account.provider_id).exists()
        if self.access_mode == self.AccessMode.SINGLE:
            return (
                self.allowed_accounts.count() == 1
                and self.allowed_accounts.filter(pk=account.pk).exists()
            )
        return self.allowed_accounts.filter(pk=account.pk).exists()
