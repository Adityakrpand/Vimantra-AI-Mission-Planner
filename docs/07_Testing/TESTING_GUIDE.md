# Testing Guide

## Backend

Run:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest --basetemp=pytest-tmp-run
```

The backend suite uses fakes for MAVSDK and does not require PX4 SITL.

Coverage areas:

- Health endpoint.
- Mission storage.
- Mission API.
- Mission upload.
- Drone connection.
- Drone actions.
- Telemetry snapshots.

## Frontend

Run:

```powershell
cd frontend
npx vitest run
npm run build
```

Coverage areas:

- Layout rendering.
- Waypoint editing.
- Mission save/load/upload.
- Drone connection controls.
- Arm/disarm/start workflow.
- Telemetry rendering.

## Workflow Verification

Backend-only:

```powershell
.\simulation\verify_px4_workflow.ps1 -SkipDroneActions
```

Full PX4 SITL:

```powershell
.\simulation\verify_px4_workflow.ps1
```

Record the full PX4 SITL result in release notes when preparing a release.
