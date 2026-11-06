"""Describe the first-party session cookie accurately in OpenAPI."""

from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class DjangoCookieAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "apps.users.authentication.CookieSessionAuthentication"
    name = "djangoSession"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": settings.SESSION_COOKIE_NAME,
            "description": (
                "Django first-party session. For POST/PUT/PATCH/DELETE also send "
                "X-CSRFToken from /auth/csrf/ (or the rotated login response)."
            ),
        }
