#!/usr/bin/env bash
# Stage 01: read-only baseline; no credentials or mutable commands
set -u
printf '%s\n' '=== AI API Maker / Stage 01 read-only audit ==='
date -u '+UTC %Y-%m-%dT%H:%M:%SZ'
printf '\n[OS]\n'
if command -v lsb_release >/dev/null 2>&1; then lsb_release -ds; else uname -sr; fi
printf '\n[RESOURCES]\n'
free -h || true
df -h / || true
printf '\n[SYSTEMD]\n'
for svc in aigetway-api aigetway-worker nginx postgresql redis-server; do
  printf '%s=' "$svc"
  systemctl is-active "$svc" 2>/dev/null || true
done
printf '\n[NGINX SYNTAX]\n'
if command -v nginx >/dev/null 2>&1; then
  nginx -t 2>&1 | sed -n '1,4p'
else printf 'nginx not on PATH\n'; fi
printf '\n[LEGACY HEALTH]\n'
curl --silent --show-error --max-time 8 https://srun.ir/aigetway/healthz 2>/dev/null | head -c 600 || true
printf '\n\n[TOOLS / VERSIONS — no tokens]\n'
for name in python3 node npm codex dsh; do
  command -v "$name" || true
done
printf '\n[LISTEN PORTS, NO PROCESS COMMAND LINES]\n'
ss -lnt 2>/dev/null | head -n 50 || true
printf '\n[IMPORTANT]\n'
printf '%s\n' 'Read-only. Do not paste credentials, browser tokens, full nginx -T, .env, or cookie files in tickets.'
