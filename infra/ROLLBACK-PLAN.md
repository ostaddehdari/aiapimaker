# Backup / Rollback contract (Stage 03 design only)

Before any deployment:
1. Record exact current Nginx config checksum and service unit checksums (read-only).
2. Create *new-app-only* PostgreSQL DB backup with a timestamp and verify it can be restored in staging.
3. Backup artifact metadata, private media files and release metadata, preserving tenant authorization.
4. Record release and migration versions; never assume all migrations safely reverse.
5. Deploy new revision to a separate path with a health probe; cutover only with explicit approval.
6. Preserve previous release and staging review evidence; validate legacy `/aigetway/healthz`.

Rollback:
1. Stop new queue admission; gracefully drain and preserve jobs.
2. Repoint only the new application's release pointer; no changes to the legacy Flask/DSH/Codex/Antigravity deployment.
3. Restart ONLY named new units under a reviewed deployment; run health and permissions checks.
4. If schema is incompatible, follow a pretested forward-fix or restore procedure approved by admin, not an ad hoc destructive downgrade.
5. Retain and audit artifacts, event logs and snapshots according to retention policy.

This file is a plan. No backup or rollback has been executed by Stage 03.
