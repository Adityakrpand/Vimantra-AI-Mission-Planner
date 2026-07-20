# Changelog

All notable changes for Vimantra AI Mission Planner are documented here.

## v1.0.0 - 2026-07-19

First stable V1 release.

### Added

- React, TypeScript, Vite, TailwindCSS, and Leaflet mission planning frontend.
- FastAPI backend with standardized API response envelopes and request IDs.
- SQLite mission persistence for create, list, load, and delete workflows.
- PX4 SITL and MAVSDK connection, upload, arm, disarm, start, and telemetry flows.
- Centralized configuration management for development, testing, and production.
- Structured logging and audit trail integration.
- Mission upload validation and pre-flight checks.
- Deterministic mission analytics and flight estimation.
- Independent V1 mission validation dashboard with readiness score, checks, errors, and warnings.
- GitHub Actions workflows for backend and frontend verification.
- Architecture, API, testing, configuration, analytics, validation, and release documentation.

### Hardened

- Frontend dev server command now binds to `127.0.0.1` consistently.
- API parsing now returns user-friendly errors for malformed responses.
- Mission Analytics and Mission Validation panels now share consistent loading, empty, and unavailable states.
- Backend package discovery includes the Sprint 17 validation package.
- FastAPI application lifecycle uses the supported lifespan API.
- PX4 workflow verification supports standardized API envelopes, explicit pre-flight checks, mission completion monitoring, and final disarm.
- Local demo data is reproducible from three realistic sample missions.

### Known Limitations

- Autonomous AI planning is intentionally reserved for the V2 roadmap.
- Full flight verification requires a running PX4 SITL instance reachable by MAVSDK.
- Hardware flight operations require operator review and environment-specific safety validation.
