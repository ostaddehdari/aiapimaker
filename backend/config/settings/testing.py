"""Isolated CI: in-memory SQLite; never connects to the production database."""

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "ci-only-django-test-secret-not-for-deployment"  # noqa: S105
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

PASSWORD_RESET_ENABLED = True
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
AUTH_LOGIN_USER_LIMIT = 3
AUTH_LOGIN_IP_LIMIT = 15
