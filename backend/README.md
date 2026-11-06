# AI API Maker — independent Django backend (Stage 04)

**Not deployed.** No routes submit work to real AI providers. Keep the existing Flask `/aigetway/` intact.

## Stack
- Django 5.2 LTS + Django REST Framework 3.17
- drf-spectacular OpenAPI and self-hosted Swagger UI assets
- PostgreSQL required in staging/production; isolated SQLite only for local development/testing
- Gunicorn/ASGI/uvicorn entrypoints available; **not running in Stage 04**

## Developer-only setup

Use a dedicated non-root virtual environment on a development machine or in CI, not the production Ubuntu services:

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
export DJANGO_SETTINGS_MODULE=config.settings.testing
python manage.py check
python manage.py test --noinput
python manage.py spectacular --file /tmp/aiapimaker-openapi.yml --validate
```

## API routes
Public probe prefix is configurable using `API_BASE_PATH`; default `/aiapimaker/api/v1/`:
- `GET /aiapimaker/api/v1/health/` — 200 service/version
- `GET /aiapimaker/api/v1/live/` — 200 process liveness
- `GET /aiapimaker/api/v1/ready/` — DB readiness, 200 or 503
- `GET /aiapimaker/api/v1/schema/` — OpenAPI
- `GET /aiapimaker/api/v1/docs/` — Swagger UI

No AI provider account, secret, production database or network API is accessed by CI.

## Settings
- `config.settings.development`: local SQLite + DEBUG, never public.
- `config.settings.testing`: in-memory SQLite, test-only key.
- `config.settings.staging`: explicit PostgreSQL URL + Django secret required.
- `config.settings.production`: explicit PostgreSQL, strong key and allowed hosts, HTTPS.

Deployment URLs are environment-driven; **the final domain is not yet decided**. Stage 04 provides API root configurable through `API_BASE_PATH` but does not change Nginx.

## Boundaries
Account schemas begin Stage 06; login Stage 07; providers Stage 11; workers Stage 21. A Plus/Pro subscription is not an unrestricted third-party API entitlement.
