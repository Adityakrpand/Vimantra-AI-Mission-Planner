# Changelog

All notable changes to this project are documented here.

This project follows [Semantic Versioning](https://semver.org/) and uses release tags in the form `vMAJOR.MINOR.PATCH` with pre-release suffixes when needed.

## [v1.0.0-rc1] - 2026-07-07

### Added

- React, TypeScript, Vite, Tailwind, and Leaflet frontend application.
- Mission planner layout with map workspace, waypoint editor, mission list, mission controls, and telemetry panel.
- FastAPI backend with health, mission, drone connection, mission upload, drone action, and telemetry endpoints.
- SQLite mission storage with schema-managed missions and waypoints.
- MAVSDK integration for PX4 SITL connection and mission execution workflow.
- Backend tests for health, mission storage, mission API, upload, drone connection, drone actions, and telemetry.
- Frontend tests for layout, telemetry rendering, mission storage actions, waypoint editing, drone connection, upload, arm/disarm, and mission start.
- PX4 SITL workflow verification script.
- Startup scripts for backend, frontend, and combined local development.
- Professional repository documentation, contribution guidance, release process, security policy, support policy, GitHub templates, workflows, and ADRs.

### Changed

- Bounded MAVSDK connection attempts with timeout handling so missing PX4 SITL fails cleanly.
- Removed nonfunctional placeholder controls from the Version 1.0 UI.

### Known Limitations

- Full PX4 SITL workflow requires a local PX4 SITL instance reachable at `udp://:14540`.
- Version 1.0 does not include AI-assisted mission planning.
- Version 1.0 is designed for local development and simulation validation, not production flight operations.
