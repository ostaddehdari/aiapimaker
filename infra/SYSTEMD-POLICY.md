# systemd & worker isolation policy (reference, NOT an active service)

Proposed units: `aiapimaker-api.service`, `aiapimaker-worker.service` and a separate, opt-in browser service. Their names must not collide with `aigetway-*` or `antigravity-*`.

## Non-root
- Service accounts: `aiapimaker-web` and `aiapimaker-worker` created only after admin approval.
- `NoNewPrivileges=true`, `PrivateTmp=true`, `ProtectSystem=strict`, `ProtectHome=true` (with explicitly scoped read/write paths).
- `ReadWritePaths` limited to allowed runtime dirs; credentials separate from app checkout.
- Set `MemoryMax`, `CPUQuota`, `TasksMax` after benchmarking against co-hosted services.
- Bind to localhost and use Nginx authentication/HTTPS only when routed publicly.
- No raw VNC ports, CDP endpoints or credential folders exposed to public interface.

## Proposed ports (must be verified on live server)
- Django staging `127.0.0.1:19361`
- React staging preview `127.0.0.1:19362`

## Environment
Use `EnvironmentFile` located outside repository with permissions 0600 (or secret manager), owned by the service administrator. Never copy secrets into source control.

## Deployment boundary
Stage 03 creates NO unit files on the live host, does not run `systemctl daemon-reload`, `enable`, `start`, `restart`, or edit Nginx.
