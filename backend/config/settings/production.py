"""Production settings: fail closed if credentials/hosts/PostgreSQL are missing."""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

if not os.getenv("DJANGO_SECRET_KEY") or len(os.environ["DJANGO_SECRET_KEY"]) < 32:
    raise ImproperlyConfigured("Production requires a strong DJANGO_SECRET_KEY")
if not os.getenv("DATABASE_URL"):
    raise ImproperlyConfigured("Production requires an explicit DATABASE_URL")
if DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":  # noqa: F405
    raise ImproperlyConfigured("Production requires PostgreSQL")
if not os.getenv("DJANGO_ALLOWED_HOSTS") or "*" in ALLOWED_HOSTS:  # noqa: F405
    raise ImproperlyConfigured("Production requires explicit DJANGO_ALLOWED_HOSTS")

DEBUG = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"


# Do not enable recovery unless a real SMTP transport is configured.
if PASSWORD_RESET_ENABLED and (
    not EMAIL_HOST or not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD
    or DEFAULT_FROM_EMAIL.endswith("@example.invalid")
):
    raise ImproperlyConfigured("Password recovery requires tested SMTP credentials and sender")
