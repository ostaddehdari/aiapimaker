# Stage 05 — React/TypeScript frontend

**State: DEMO ONLY.** Stage 05 builds the visual shell for AI API Maker. It is not deployed and has no real Django authentication or provider connectivity.

## Stack
- React 19 + Vite 8 + TypeScript + React Router
- RTL Persian with **locally bundled Vazirmatn** from `@fontsource/vazirmatn` (SIL OFL); Font Awesome individual icons
- GSAP sidebar collapse and reduced-motion fallback
- Responsive mobile drawer, keyboard navigation and skip-link, theme toggle, CSS design tokens

## Demo routes
- `/login`: disabled credential inputs and clearly marked role preview links. These links are **not access controls**.
- `/admin`, `/admin/providers`, `/admin/users`, `/admin/supervisor`: static shell and safe placeholders.
- `/app`: chat composer with local-only demo response.
- `/app/accounts`, `/app/api-tokens`: placeholders.

**Never publish the demo admin routes as a functional administration portal until real Django session authentication and object-level permissions are delivered in Stages 07–09.**

## Local dev instructions
```bash
cd frontend
npm install
npm run lint
npm run test
npm run build
npm run dev
```
The local development URL is `http://127.0.0.1:19362/aiapimaker/`. Use a development machine rather than the production Ubuntu VPS for full npm work.

## Base path and final domain
The domain is not final. Configurable Vite base and Router basename are derived from `VITE_BASE_PATH`:
```bash
VITE_BASE_PATH=/aiapimaker/ npm run build
VITE_BASE_PATH=/ npm run build
VITE_BASE_PATH=/newname/ npm run build
```
`VITE_API_BASE_PATH` is reserved for future Django API connectivity. No domain names are embedded in runtime code.

## Acceptance
- `npm run build` validates TS + bundle; `npm run test` runs component tests for brand, demo login, local chat and base paths.
- CI builds under both `/aiapimaker/` and `/`.
- Visual breakpoints at 375px / 768px / 1440px still need manual browser screenshots.
- No changes to Nginx, systemd, PostgreSQL, Redis, Codex, DSH, or Antigravity.
