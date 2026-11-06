# Backend — Django API

Scope: Django REST Framework owns every new AI API Maker endpoint, authorization, tenancy, provider/account registry and artifact metadata.

Stage 04 will bootstrap the actual Django application. Do not reuse or replace the legacy Flask server.

Operational rule: API secrets and settings are provided through environment variables or a secure secrets store, never committed.
