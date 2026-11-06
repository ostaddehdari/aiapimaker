"""Local development only. Never bind this configuration to the public internet."""

from .base import *  # noqa: F403

DEBUG = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
