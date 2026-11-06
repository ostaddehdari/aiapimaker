# AI API Maker

> Multi-tenant AI orchestration platform — React + Django + PostgreSQL
>
> **Production target:** `https://srun.ir/aiapimaker/`
>
> **Status:** Stage 01 audit active; Stage 02 repo tooling in review. No new service deployed. No production deployment has occurred.

## Roadmap
- [40 stages / 320 work items](docs/ROADMAP-40-STAGES.md)
- [Architecture and hard constraints](docs/ARCHITECTURE.md)
- [Stage 01 execution playbook](docs/STAGE-01-PLAYBOOK.md)
- [Stage 02 repository conventions](docs/BRANCHING-AND-RELEASES.md)
- [Stage completion checklist](docs/STAGE-EXIT-CRITERIA.md)
- [Draft Django API contract](docs/API-CONTRACT-DRAFT.md)

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
