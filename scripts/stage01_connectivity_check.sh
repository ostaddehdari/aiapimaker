#!/usr/bin/env bash
# Safe, read-only Stage 01 check for SSH resets and current resource pressure.
# No credentials, cookies, environment values, raw journal entries or process arguments are emitted.
set -u
printf '%s\n' '=== Stage 01 / connectivity and memory (READ-ONLY) ==='
date -u '+UTC %Y-%m-%dT%H:%M:%SZ'
printf '\n[STORAGE]\n'
df -h /
printf '\n[MEMORY]\n'
free -h
printf '\n[SWAP PRESSURE: si and so should be interpreted from interval rows]\n'
if command -v vmstat >/dev/null 2>&1; then vmstat 1 5; fi
printf '\n[CORE SERVICE HEALTH]\n'
for service in ssh nginx postgresql redis-server aigetway-api aigetway-worker antigravity-gateway-api antigravity-gateway-worker; do
  printf '%s=' "$service"
  systemctl is-active "$service" 2>/dev/null || true
done
printf '\n[LEGACY HTTP HEALTH]\n'
curl --silent --show-error --max-time 8 https://srun.ir/aigetway/healthz 2>/dev/null | head -c 300 || true
printf '\n\n[KERNEL OOM EVENT COUNT LAST 3 HOURS — no raw log]\n'
if command -v journalctl >/dev/null 2>&1; then
  journalctl -k --since '-3 hours' --no-pager -o cat 2>/dev/null | grep -Eic 'out of memory|oom-killer|killed process' || true
fi
printf '\n[PORT 2233 LISTENER]\n'
ss -lnt 2>/dev/null | awk 'NR==1 || $4 ~ /:2233$/'
printf '\n[NOTE] Do not infer SSH reset cause from this snapshot alone; do not execute swapoff, prune, restart, or upgrades based on it.\n'
