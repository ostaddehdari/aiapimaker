"""Database-backed login throttling with HMAC user/IP fingerprints."""

import hashlib
import hmac
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .security_models import LoginThrottle


def _fingerprint(kind: str, value: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        f"{kind}:{value}".encode(),
        hashlib.sha256,
    ).hexdigest()


def login_identifiers(request, username: str) -> tuple[tuple[str, int], ...]:
    # REMOTE_ADDR is safe from spoofed X-Forwarded-For, but a reverse proxy
    # must configure a trusted real-ip policy to avoid a shared localhost bucket.
    remote = str(request.META.get("REMOTE_ADDR", "unknown"))
    return (
        (_fingerprint("ip", remote), settings.AUTH_LOGIN_IP_LIMIT),
        (_fingerprint("user", username.casefold().strip()), settings.AUTH_LOGIN_USER_LIMIT),
    )


def check_login_allowed(keys: tuple[tuple[str, int], ...]) -> bool:
    now = timezone.now()
    for fingerprint, _ in keys:
        record = LoginThrottle.objects.filter(pk=fingerprint).first()
        if record is not None and record.blocked_until and record.blocked_until > now:
            return False
    return True


def note_failed_login(keys: tuple[tuple[str, int], ...]) -> None:
    now = timezone.now()
    with transaction.atomic():
        for fingerprint, limit in sorted(set(keys)):
            row, _ = LoginThrottle.objects.select_for_update().get_or_create(
                fingerprint=fingerprint,
            )
            elapsed = (now - row.window_started).total_seconds()
            if elapsed >= settings.AUTH_THROTTLE_WINDOW_SECONDS:
                row.window_started = now
                row.failures = 0
                row.blocked_until = None
            row.failures += 1
            if row.failures >= limit:
                row.blocked_until = now + timedelta(seconds=settings.AUTH_LOCK_SECONDS)
            row.save(update_fields=["window_started", "failures", "blocked_until", "updated_at"])


def note_successful_login(keys: tuple[tuple[str, int], ...]) -> None:
    # Reset only the user fingerprint. Keep IP-level failure history.
    LoginThrottle.objects.filter(pk=keys[1][0]).delete()
