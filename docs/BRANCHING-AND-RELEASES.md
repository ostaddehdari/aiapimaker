# Branch and release policy

## Branches
- `main`: production baseline. No direct unreviewed pushes.
- `stage/01-audit-baseline`: pending Stage 01 audit completion.
- `stage/02-repository-foundation`: based on Stage 01; documentation/tooling only.
- Future stages: prefer fresh branches from the last approved stage; PRs must show their dependency chain.

## Configure GitHub repository rules (administrator)
In repository settings → Rules → Rulesets, create protection for `main`:
- Require a pull request before merging (at least one review).
- Require passing status check `Repository verification / validate` (after first workflow run; use actual published name).
- Block force pushes and deletion of `main`.
- Require conversation resolution. Consider signed commits and two reviewers for infra/credential changes.

A ruleset can only be marked 'enabled' after an administrator verifies it in GitHub; this file does not claim a rule is active.

## Versioning
Semantic version `MAJOR.MINOR.PATCH` for independently releasable product. Current repository tooling starts at `0.1.0-dev`; it is NOT a live production release.
- New API route or compatible feature: MINOR.
- Backward-compatible fixes: PATCH.
- Incompatible API contract: MAJOR and migration document.
- Each Stage completion is a milestone, not necessarily a new SemVer release.

## Release protocol
1. Merged code + tests + evidence.
2. Staging deployment, health and backward compatibility checks.
3. Backup database, uploads, configuration (without committing secrets).
4. Production release only with explicit approval and rollback plan.
5. Confirm legacy Flask/DSH/Codex/Antigravity still healthy.
6. Note deployment URL (currently **pending change**); do not hardcode `srun.ir/aiapimaker`.

## Change log
Keep `CHANGELOG.md` updated. Include user-visible features and security changes, excluding secrets.
