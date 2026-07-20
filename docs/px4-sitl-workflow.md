# PX4 SITL Workflow Verification

This module verifies the planned Vimantra flow:

1. Backend health is reachable.
2. A mission can be created and loaded.
3. Drone status and telemetry endpoints respond.
4. With PX4 SITL running, the app can connect, verify telemetry, run pre-flight checks, upload, arm, start, monitor mission completion, and disarm.

## Backend-only check

Use this when PX4 SITL is not running. It verifies the API and mission storage parts without sending drone commands.

```powershell
.\simulation\verify_px4_workflow.ps1 -SkipDroneActions
```

Expected result:

- `/health` returns `ok`.
- A verification mission is saved and loaded.
- `/drone/status` responds.
- `/drone/telemetry` responds with a disconnected snapshot.

## Full PX4 SITL check

Start PX4 SITL first, then run:

```powershell
.\simulation\verify_px4_workflow.ps1
```

The default MAVSDK address is:

```text
udp://:14540
```

Use a different address only if PX4 is exposing MAVLink elsewhere:

```powershell
.\simulation\verify_px4_workflow.ps1 -SystemAddress "udp://:14540"
```

If the backend is reachable but PX4 is slow to respond, adjust the HTTP guard:

```powershell
.\simulation\verify_px4_workflow.ps1 -ApiTimeoutSeconds 45
```

## What The Script Does

The script calls the same backend endpoints used by the frontend:

- `GET /health`
- `POST /missions`
- `GET /missions/{mission_id}`
- `GET /drone/status`
- `GET /drone/telemetry`
- `POST /drone/connect`
- `POST /missions/{mission_id}/preflight`
- `POST /missions/{mission_id}/upload`
- `POST /drone/arm`
- `POST /drone/start-mission`
- repeated `GET /drone/telemetry` calls until mission completion
- `POST /drone/disarm`
- `DELETE /missions/{mission_id}` to remove verification data

## Pass Criteria

The workflow passes when:

- PX4 connection returns `connected: true`.
- Mission upload returns `uploaded: true`.
- Arm returns `completed: true`.
- Start mission returns `completed: true`.
- Telemetry returns `connected: true` with position, altitude, speed, mode, and mission progress.
- Mission progress reaches the reported total before the configured timeout.
- Disarm returns `completed: true`.
- The temporary verification mission is removed.

## Current Scope

This is a verification module only. It does not add new planner features, autonomous logic, AI behavior, or flight modes beyond the Version 1.0 plan.
