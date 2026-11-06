"""Isolated CI: in-memory SQLite; never connects to the production database."""

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "ci-only-django-test-secret-not-for-deployment"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
