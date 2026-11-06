#!/usr/bin/env bash
# Stage 01 follow-up: strictly read-only inspection, no services altered.
set -u
echo '=== AI API Maker Stage 01 follow-up (READ ONLY) ==='
date -u '+UTC %Y-%m-%dT%H:%M:%SZ'
echo '[DISK AND INODES]'
df -h /; df -i /
echo '[TARGETED STORAGE SIZES, no deletions]'
for dir in /var/log /var/backups /var/cache /var/lib/docker /var/lib/containers /var/lib/postgresql /var/lib/aigetway /root/.npm /root/.cache /opt; do
  if [ -d "$dir" ]; then
    du -shx "$dir" 2>/dev/null || true
  fi
done
echo '[JOURNAL SIZE]'
if command -v journalctl >/dev/null 2>&1; then journalctl --disk-usage 2>/dev/null || true; fi
echo '[MEMORY / SWAP PRESSURE — si,so are swap-in/out rates]'
if command -v vmstat >/dev/null 2>&1; then vmstat 1 3; fi
echo '[TOP RSS PROCESS NAMES, no command line arguments]'
ps -eo pid,comm,rss --sort=-rss 2>/dev/null | head -n 16 || true
echo '[AI SERVICE UNITS (NAMES ONLY)]'
systemctl list-unit-files --type=service --no-pager --no-legend 2>/dev/null | awk '{print $1}' | grep -Ei '(aigetway|antigrav|codex|deepseek|dsh)' || true
echo '[RELEVANT NGINX ROUTES ONLY]'
if command -v nginx >/dev/null 2>&1; then
  nginx -T 2>/dev/null | grep -E '^[[:space:]]*location[[:space:]]+([^[:space:]]+[[:space:]]+)?/(aigetway|aiapimaker)' || true
fi
echo '[TOOL VERSIONS]'
for cmd in codex dsh; do
  if command -v "$cmd" >/dev/null 2>&1; then "$cmd" --version 2>/dev/null | head -n 1 || true; fi
done
echo '[NOTE] Read-only. Review output before sharing. No .env/cookies/auth files should be exposed.'
