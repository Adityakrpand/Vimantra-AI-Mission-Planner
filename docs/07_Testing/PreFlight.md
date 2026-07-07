# Pre-Flight Checks

Sprint 15 adds a reusable pre-flight check system before mission upload and mission start.

## Flow

```text
Mission -> Validation -> Pre-Flight -> Upload -> Arm -> Start
```

Mission upload and mission start are blocked when any mandatory check fails.

## Mandatory Checks

- Vehicle Connected
- Mission Valid
- GPS Fix Available
- Battery Available
- Telemetry Active
- Flight Controller Reachable
- Mission Loaded
- Home Position Available
- Configuration Loaded

## Optional Checks

Optional checks create warnings and reduce the score, but do not block readiness:

- Battery Above Warning Threshold
- Strong GPS Signal
- Compass Healthy
- Mission Distance Warning

## Configuration

```text
VIMANTRA_PREFLIGHT_BATTERY_WARNING_THRESHOLD_PERCENT=30
VIMANTRA_PREFLIGHT_GPS_MINIMUM_SATELLITES=6
VIMANTRA_PREFLIGHT_OPTIONAL_CHECKS_ENABLED=true
```

## API

Run pre-flight checks for a saved mission:

```text
POST /missions/{mission_id}/preflight
```

The response is returned inside the standard API envelope:

```json
{
  "ready": true,
  "score": 100,
  "checks": [
    {
      "name": "GPS Fix Available",
      "status": "PASS",
      "mandatory": true,
      "message": "GPS fix is available."
    }
  ],
  "warnings": []
}
```

## Testing

Backend tests cover:

- Disconnected drone
- Invalid mission
- No telemetry
- No GPS
- Successful pre-flight

Run:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest --basetemp=pytest-tmp-run
```
