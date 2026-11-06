# AI API Maker

> Multi-tenant AI orchestration platform — React + Django + PostgreSQL
>
> **Temporary historical target:** `https://srun.ir/aiapimaker/` — the final domain has not been selected.
>
> **Status:** Stages 01–05 in review; Stage 06 multi-tenant PostgreSQL schema in CI/review. No new service deployed.

## Roadmap
- [40 stages / 320 work items](docs/ROADMAP-40-STAGES.md)
- [Architecture and hard constraints](docs/ARCHITECTURE.md)
- [Stage 01 execution playbook](docs/STAGE-01-PLAYBOOK.md)
- [Stage 02 repository conventions](docs/BRANCHING-AND-RELEASES.md)
- [Stage completion checklist](docs/STAGE-EXIT-CRITERIA.md)
- [Draft Django API contract](docs/API-CONTRACT-DRAFT.md)
- [Stage 05 UI acceptance and scope](docs/STAGE-05-UI-ACCEPTANCE.md)

## Stack
- React + TypeScript + Vite; Persian RTL layout; Vazirmatn/Vazir; Font Awesome; GSAP (respect reduced motion)
- Django + Django REST Framework + PostgreSQL
- Redis + Celery for durable asynchronous processing; Channels/SSE for progress
- Scoped API tokens, provider accounts, per-account isolated profiles, browser workers where authorized
- Nginx reverse proxy under `/aiapimaker/`; independent Django and React releases

## Existing installations — DO NOT REPLACE
The existing `/aigetway/` (Flask/Codex), DeepSeek Harness, and Antigravity installation must remain running. Antigravity authentication has not yet been confirmed. The new system integrates them through adapters and a staged migration. Never overwrite their credentials or service units. Preserve rollback.

## Safety, licensing and account access
This platform does not treat personal ChatGPT Plus/Pro subscriptions as OpenAI API entitlements or a reusable pool for bypassing usage limits. Provider-account access is permission-scoped, tenant-isolated, and dependent on each provider's supported interface and terms. Browser automation of third-party chats is only enabled where authorized; do not bypass CAPTCHA, MFA, rate limits, or subscriptions.

## Implementation gates
Every stage has exactly eight checkbox work items and a Definition of Done. No stage is DONE without evidence: tests, screenshots/logs where appropriate, rollback and documentation. Keep secrets out of Git.

## Development workflow
1. Read the roadmap and Stage 01 playbook.
2. Implement on a feature branch `stage/01-audit-baseline`, not directly on production.
3. Add verification artifacts to PR and obtain review.
4. Deploy to staging first. Production cutover requires explicit go/no-go.

**Current public URL is a deployment target, not a claim that this new application is online.**

## Independent application structure (Stage 02)

| Folder | Purpose |
|---|---|
| `backend/` | Django/DRF (Stage 04) |
| `frontend/` | React/TypeScript (Stage 05) |
| `workers/` | Celery and Supervisor |
| `connectors/` | Account-scoped and authorized provider integrations |
| `infra/` | Nginx/systemd templates, staging and rollback |
| `tests/` | Shared tests and fixtures |

Setup and contribution guidance: [CONTRIBUTING.md](CONTRIBUTING.md). Target public domain/URL is **not final**; deployment must read it from configuration.

## Stage 04 — Django API (not deployed)

The new [Django backend](backend/README.md) provides `health/`, `live/`, `ready/` and OpenAPI routes under configurable `API_BASE_PATH`. Runtime requirements are isolated to `backend/requirements.txt`. For safe CI run:

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python manage.py check --settings=config.settings.testing
python manage.py test apps.core --noinput --settings=config.settings.testing
```

Production credentials, Django/PostgreSQL installation, Nginx routing and final domain setup are deferred to a later, explicitly approved deployment stage.

## Stage 05 — React frontend preview (not deployed)

The independent [React demo](frontend/README.md) provides a Persian RTL login preview, admin/user shells, right collapsible GSAP sidebar, theme switcher and local-only chat demo. **No functional authentication or real API access exists in these preview routes**; do not expose them as a production admin site.

```bash
cd frontend
npm install
npm run lint
npm run test
VITE_BASE_PATH=/aiapimaker/ npm run build
VITE_BASE_PATH=/ npm run build
```

CI runs these steps separately from the production VPS. Site name and public base path remain configurable.

## Stage 06 — independent PostgreSQL schema (not deployed)

The [data model and migration plan](docs/STAGE-06-DATA-MODEL.md) includes UUID users/tenants, multiple provider accounts, hashed scoped API token metadata, chats/messages, jobs/leases and private artifacts. Django-generated migrations and safe **disabled** provider seeds are committed.

CI verifies fresh migrations, reversible seed/artifact schema steps and owner-isolation tests on disposable PostgreSQL 16. This does not create any database or alter `/aigetway/` on the production server. Permission-enforced user dashboards and real providers remain future work.
