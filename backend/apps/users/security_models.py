"""Session inventory and throttling for first-party Django authentication.

Never store plaintext passwords, bearer tokens, browser cookies or IPs here.
"""

import hashlib
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


def session_digest(session_key: str) -> str:
    return hashlib.sha256(session_key.encode("utf-8")).hexdigest()


class AuthDeviceSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="auth_devices")
    session_hash = models.CharField(max_length=64, unique=True, editable=False)
    label = models.CharField(max_length=90, default="مرورگر")
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "revoked_at"], name="iam_device_user_revoked"),
            models.Index(fields=["expires_at"], name="iam_device_expiry"),
        ]

    @property
    def active(self):
        return self.revoked_at is None and self.expires_at > timezone.now()


class LoginThrottle(models.Model):
    """Fixed-window database throttle. Use indexed HMAC identifiers, not usernames/IPs."""

    fingerprint = models.CharField(max_length=64, primary_key=True)
    failures = models.PositiveIntegerField(default=0)
    window_started = models.DateTimeField(default=timezone.now)
    blocked_until = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class AuthEvent(models.Model):
    """No passwords, raw IPs, tokens, email addresses, or cookies are logged."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="auth_events",
    )
    event = models.CharField(max_length=40)
    identifier_hash = models.CharField(max_length=64, blank=True)
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "-created_at"], name="iam_audit_user_created"),
            models.Index(fields=["event", "-created_at"], name="iam_audit_event_created"),
        ]

    @classmethod
    def record(cls, event, request, *, user=None, identifier="", success=False):
        cls.objects.create(
            user=user,
            event=event,
            identifier_hash=identifier[:64],
            success=success,
        )
