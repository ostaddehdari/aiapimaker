"""Revoke first-party Django sessions on every authenticated API request."""

from django.conf import settings
from django.contrib.auth import logout
from django.http import JsonResponse
from django.utils import timezone

from .security_models import AuthDeviceSession, session_digest


class TrackedSessionMiddleware:
    """Reject untracked/revoked sessions; legacy Django admin is unaffected."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(settings.API_BASE_PATH) and request.user.is_authenticated:
            key = request.session.session_key
            allowed = bool(
                key
                and AuthDeviceSession.objects.filter(
                    user=request.user,
                    session_hash=session_digest(key),
                    revoked_at__isnull=True,
                    expires_at__gt=timezone.now(),
                ).exists()
            )
            if not allowed:
                logout(request)
                return JsonResponse(
                    {"error": {"code": "session_expired", "message": "Session expired or revoked"}},
                    status=401,
                )
        return self.get_response(request)
