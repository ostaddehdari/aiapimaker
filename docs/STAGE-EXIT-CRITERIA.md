# Stage completion / Definition of Done

A stage is **DONE** only when:
- [ ] Every one of its eight Work IDs is implemented and checked; blockers explicitly labelled.
- [ ] Relevant unit, contract, integration or E2E tests are run and recorded.
- [ ] New endpoints and configuration variables are documented and versioned.
- [ ] Security review covers token/cookie/session handling and per-user authorization.
- [ ] Memory/disk/browser limits documented if task adds worker or Chromium.
- [ ] Staging build/deployment (when relevant) validated; no implicit production changes.
- [ ] Rollback tested or described; old `/aigetway/` smoke tests unaffected.
- [ ] PR reviewed and CI passed, then issue closed with evidence.

**Statuses:** TODO → IN_PROGRESS → REVIEW → VERIFIED → DONE. Use BLOCKED for policy/credential/external-service dependencies.

## Evidence minimum
Issue comments should include precise commit/PR, test command and observed result, comparison to acceptance criteria, and known risk. Do not put credentials, OAuth responses or cookie values in public issues.

## Stage 02 acceptance
1. Modular directories exist.
2. Git workflow and ruleset plan documented.
3. Contribution, CODEOWNERS, Issue and PR templates exist.
4. Ignore patterns for secrets/session browser profiles exist.
5. SemVer/changelog documented.
6. A reusable Stage DoD checklist exists.
7. Formatting/lint/pre-commit configs exist.
8. CI jobs check repository shape, Python/shell syntax and secrets.

Stage 02 can be reviewed independently but **cannot be deployed** until Stage 01 operational gate is passed.
