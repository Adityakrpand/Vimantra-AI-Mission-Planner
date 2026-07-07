# Vimantra AI Mission Planner

Vimantra AI Mission Planner is a local ground-control mission planning application for PX4 SITL. Version `v1.0.0-rc1` includes a React mission-planning frontend, a FastAPI backend, SQLite mission storage, MAVSDK integration, PX4 SITL workflow support, mission upload/execution controls, and telemetry monitoring.

Version 1.0 does not implement autonomous AI planning. AI mission planning is reserved for the Version 2.0 roadmap.

## Capabilities

- Plan waypoint missions on a Leaflet map.
- Add, edit, save, load, and clear waypoint missions.
- Persist missions in SQLite.
- Connect to PX4 SITL through MAVSDK.
- Upload missions to a connected drone system.
- Validate missions before upload.
- Arm, disarm, and start missions.
- Monitor telemetry for position, altitude, speed, heading, battery, GPS fix, flight mode, and mission progress.
- Verify the local backend-only workflow and the PX4 SITL workflow with repeatable scripts.

## Repository Structure

```text
.github/      GitHub workflows, issue templates, pull request template
assets/       Project media, screenshots, diagrams, and branding assets
backend/      FastAPI API, MAVSDK integration, domain services, tests
database/     SQLite schema and generated local mission database location
docs/         Engineering, architecture, testing, deployment, and user docs
examples/     Example missions, requests, and integration notes
frontend/     React, TypeScript, Vite, Tailwind, Leaflet application
missions/     Local mission artifacts and exported mission files
scripts/      Local developer startup helpers
simulation/   PX4 SITL workflow verification scripts
```

## Quick Start

Start backend and frontend from the repository root:

```powershell
.\scripts\start_app.ps1
```

Local URLs:

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`

Start services separately when debugging:

```powershell
.\scripts\start_backend.ps1
.\scripts\start_frontend.ps1
```

## Configuration

Configuration is environment-driven. Backend settings are loaded from environment variables and optional env files in this order:

1. Built-in defaults.
2. `.env`
3. `.env.<environment>`, such as `.env.development`, `.env.testing`, or `.env.production`.
4. Process environment variables.

Copy the examples before editing local settings:

```powershell
Copy-Item .env.example .env
Copy-Item frontend/.env.example frontend/.env
```

Important backend variables:

- `VIMANTRA_ENV`: `development`, `testing`, or `production`.
- `VIMANTRA_API_HOST` and `VIMANTRA_API_PORT`: API bind address.
- `VIMANTRA_DATABASE_PATH`: SQLite mission database path.
- `VIMANTRA_MAVSDK_ADDRESS`: default MAVSDK connection address.
- `VIMANTRA_DRONE_CONNECTION_TIMEOUT_SECONDS`: PX4 connection timeout.
- `VIMANTRA_TELEMETRY_READ_TIMEOUT_SECONDS`: telemetry stream read timeout.
- `VIMANTRA_MISSION_UPLOAD_TIMEOUT_SECONDS`: MAVSDK mission upload timeout.
- `VIMANTRA_VALIDATION_*`: mission validation limits and warning thresholds.

Important frontend variable:

- `VITE_API_BASE_URL`: backend API base URL.

To change the MAVSDK address:

```powershell
$env:VIMANTRA_MAVSDK_ADDRESS = "udp://:14540"
```

To change validation limits, edit `.env`:

```text
VIMANTRA_VALIDATION_MINIMUM_ALTITUDE_METERS=5
VIMANTRA_VALIDATION_MAXIMUM_ALTITUDE_METERS=120
VIMANTRA_VALIDATION_MINIMUM_SPEED_METERS_PER_SECOND=1
VIMANTRA_VALIDATION_MAXIMUM_SPEED_METERS_PER_SECOND=15
```

Invalid configuration fails application startup with a clear validation error. See [docs/08_Deployment/Configuration.md](docs/08_Deployment/Configuration.md).

## Verification

Backend tests:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest --basetemp=pytest-tmp-run
```

Frontend tests:

```powershell
cd frontend
npx vitest run
```

Frontend production build:

```powershell
cd frontend
npm run build
```

Backend-only workflow verification:

```powershell
.\simulation\verify_px4_workflow.ps1 -SkipDroneActions
```

Full PX4 SITL verification, after PX4 is running on the default MAVSDK address `udp://:14540`:

```powershell
.\simulation\verify_px4_workflow.ps1
```

## Engineering Standards

This repository follows:

- Semantic Versioning.
- Conventional Commits.
- GitHub Flow with protected merge validation.
- Architecture Decision Records.
- Python type hints and pytest coverage for backend behavior.
- TypeScript, React Testing Library, and production builds for frontend behavior.

## Mission Validation

Every mission must pass the Mission Validation Engine before upload to PX4. The validator is independent from the upload service and is reusable for future AI-generated missions.

Validation endpoint:

```text
POST /api/missions/validate
```

Validation checks include waypoint count, required mission name, required waypoint values, latitude/longitude ranges, configured altitude and speed limits, duplicated consecutive waypoints, and zero-distance missions. Warnings are returned separately and do not block upload.

See [CONTRIBUTING.md](CONTRIBUTING.md), [ARCHITECTURE.md](ARCHITECTURE.md), [RELEASE_PROCESS.md](RELEASE_PROCESS.md), and [docs/12_Developer_Guide/README.md](docs/12_Developer_Guide/README.md).

## Release Status

Current release candidate: `v1.0.0-rc1`.

The application is ready for local evaluation and PX4 SITL validation. The only external runtime requirement for the complete flight workflow is a running PX4 SITL instance reachable by MAVSDK.

## Maintainer

- [Aditya K. R. Pand](https://github.com/Adityakrpand)
