# Changelog

All notable changes to this repository will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and Semantic Versioning.

## [Unreleased]
### Added
- Stage 01 non-mutating Ubuntu audit procedures and baseline.
- 40-stage, 320-task implementation plan.
- Stage 02 repository structure and collaboration/validation tooling.
- Stage 04 independent Django API scaffold, isolated CI checks and OpenAPI probes.
- Stage 05 React/Vite visual frontend with RTL Vazirmatn, responsive GSAP sidebar, dark/light themes and demo-only login/chat shells.
- Stage 06 PostgreSQL schema/migrations for independent tenant, provider, account, chat, token and job metadata.
- Stage 07 first-party Django session authentication with CSRF, device revocation, login throttling, audit events and opt-in password reset (not deployed).
### Security
- Secrets, session profiles, uploads and local credentials excluded from version control.
### Infrastructure
- Public domain and React/Django base path are configurable; actual production host is **not yet decided**.

## [0.1.0-dev] — repository preparation
- Initial planning and issue tracking only; **no app released**.
