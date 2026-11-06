# Contributing to AI API Maker

## Working agreements

1. Only implement one stage per feature branch. Use `stage/NN-short-name`.
2. Stage 01 audit is read-only; Stage 02 repository work does not deploy.
3. Never commit `.env`, session/cookie folders, OAuth tokens, API keys, files from noVNC or customer artifacts.
4. Retain existing Codex, DeepSeek Harness, Antigravity and `/aigetway/` until an explicitly approved migration.
5. Every PR must link its Stage issue, tests, rollback steps, affected interfaces and any blocked third-party provider permission.
6. Do not use user ChatGPT Plus/Pro account sessions as a replacement for official OpenAI API or to bypass account usage restrictions.
7. Run: `python3 scripts/verify_repository.py`, `ruff check .`, `ruff format --check .` and `bash -n scripts/*.sh` (when tools are installed).
8. PRs must pass CI before review. Avoid direct pushes to `main`; admins should enable required reviews and checks in GitHub branch settings.

## Branch flow

`main` is protected production baseline, `stage/NN-feature` is test-only. During this kickoff, Stage 02 is based on Stage 01 and its PR target must be Stage 01 until Stage 01 lands on main. Do not squash stages into unrelated deployments.

## Evidence

Commit tests/screenshots with synthetic data only. Never post JWT, TOTP, account cookies, auth.json, full private nginx config, personal email or SSH keys in issues.

See [workflow policy](docs/BRANCHING-AND-RELEASES.md) and [completion checklist](docs/STAGE-EXIT-CRITERIA.md).
