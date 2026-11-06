"""DRF session auth with an explicit 401 challenge for anonymous API clients."""

from rest_framework.authentication import SessionAuthentication


class CookieSessionAuthentication(SessionAuthentication):
    def authenticate_header(self, request):
        # Return HTTP 401 rather than DRF's default anonymous HTTP 403.
        # This does NOT disable CSRF enforcement for authenticated requests.
        return "Session"
