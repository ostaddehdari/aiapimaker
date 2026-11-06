"""Staging: requires explicit secret and PostgreSQL. No public TLS redirect."""

import os

from django.core.exceptions import ImproperlyConfigured

from . import base as base_settings
from .base import *  # noqa: F403

if not os.getenv("DJANGO_SECRET_KEY"):
    raise ImproperlyConfigured("DJANGO_SECRET_KEY is required for staging")
if DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":  # noqa: F405
    raise ImproperlyConfigured("PostgreSQL DATABASE_URL is required for staging")

DEBUG = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False  # Localhost testing before an approved HTTPS proxy.
SECURE_CONTENT_TYPE_NOSNIFF = True


# Do not enable recovery unless a real SMTP transport is configured.
if base_settings.PASSWORD_RESET_ENABLED and (
    not base_settings.EMAIL_HOST
    or not base_settings.EMAIL_HOST_USER
    or not base_settings.EMAIL_HOST_PASSWORD
    or base_settings.DEFAULT_FROM_EMAIL.endswith("@example.invalid")
):
    raise ImproperlyConfigured("Password recovery requires tested SMTP credentials and sender")
