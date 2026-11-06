#!/usr/bin/env bash
# Read-only staging preflight for AI API Maker. No installs, writes, restarts or config changes.
set -u

warn=0
blocked=0

say() { printf '%s\n' "$*"; }
ok() { say "CHECK_PASS: $*"; }
warning() { warn=$((warn+1)); say "CHECK_WARN: $*"; }
block() { blocked=$((blocked+1)); say "CHECK_BLOCKED: $*"; }

say "=== Stage 03 / local staging preflight — READ ONLY ==="
date -u '+UTC %Y-%m-%dT%H:%M:%SZ'

for file in infra/staging.env.example docs/STAGE-03-STAGING-PLAN.md infra/ROLLBACK-PLAN.md infra/SYSTEMD-POLICY.md; do
  if [ -f "$file" ]; then ok "template found: $file"; else block "missing template: $file"; fi
done

for unit in nginx postgresql redis-server aigetway-api aigetway-worker; do
  if systemctl is-active --quiet "$unit" 2>/dev/null; then
    ok "legacy unit active: $unit"
  else
    warning "unit not active or inaccessible: $unit"
  fi
done

if command -v ss >/dev/null 2>&1; then
  for port in 19361 19362; do
    if ss -lnt 2>/dev/null | awk 'NR>1 {print $4}' | grep -Eq ":${port}$"; then
      block "candidate localhost port $port already in use; choose another"
    else
      ok "candidate port $port not observed in LISTEN list"
    fi
  done
else
  warning "ss unavailable; proposed ports are UNVERIFIED"
fi

if command -v python3 >/dev/null 2>&1; then
  python3 --version
  if python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
    ok "Python >=3.11"
  else block "Python <3.11"; fi
else block "python3 not installed"; fi

if command -v node >/dev/null 2>&1; then
  node --version
  if node -e 'process.exit(Number(process.versions.node.split(".")[0]) >= 22 ? 0 : 1)'; then
    ok "Node.js >=22"
  else warning "Node.js <22 in current PATH; use isolated runtime"; fi
else warning "node not found in current PATH"; fi

if command -v psql >/dev/null 2>&1; then
  psql --version
  version=$(psql --version | awk '{print $3}' | cut -d. -f1)
  if [ "$version" -ge 14 ] 2>/dev/null; then ok "PostgreSQL CLI >=14"; else warning "PostgreSQL CLI <14 or unknown"; fi
else warning "psql client not found; server may still be running"; fi

avail_kib=$(df -Pk / 2>/dev/null | awk 'NR==2 {print $4}')
if [ -z "$avail_kib" ]; then
  warning "could not read available disk"
elif [ "$avail_kib" -lt 10485760 ]; then
  block "under 10GiB available disk"
elif [ "$avail_kib" -lt 20971520 ]; then
  warning "under recommended 20GiB free disk; no production browser workers"
else
  ok "disk >=20GiB free"
fi

say "CHECK_SUMMARY: blocked=$blocked warnings=$warn"
if [ "$blocked" -gt 0 ]; then
  say "STAGING_PREFLIGHT_BLOCKED: do not deploy"
  exit 2
fi
if [ "$warn" -gt 0 ]; then
  say "STAGING_PREFLIGHT_PASS_WITH_WARNINGS: no deploy authorized"
  exit 0
fi
say "STAGING_PREFLIGHT_PASS: no deploy authorized"
