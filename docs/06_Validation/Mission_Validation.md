# Mission Validation Engine

## Architecture

Sprint 17 adds an independent validation package under `backend/validation`.
It does not import mission analytics or pre-flight services.

- `config.py`: typed validation thresholds.
- `models.py`: API response, issue, check, and summary models.
- `rules.py`: deterministic rule calculations.
- `validator.py`: rule orchestration, score, status, and logging.

## Validation Rules

The engine validates waypoint count, coordinate ranges, duplicate consecutive
waypoints, mission distance, single-leg distance, waypoint spacing, altitude
limits, altitude jumps, climb and descent rate, speed limits, cruise speed,
flight duration, battery usage, reserve battery, path validity, and sharp turns.

## Configuration

All thresholds come from environment-backed application settings.

```text
VIMANTRA_VALIDATION_ENGINE_MINIMUM_WAYPOINTS=2
VIMANTRA_VALIDATION_ENGINE_MAXIMUM_WAYPOINTS=100
VIMANTRA_VALIDATION_ENGINE_MINIMUM_ALTITUDE_METERS=5
VIMANTRA_VALIDATION_ENGINE_MAXIMUM_ALTITUDE_METERS=120
VIMANTRA_VALIDATION_ENGINE_MAXIMUM_ALTITUDE_JUMP_METERS=60
VIMANTRA_VALIDATION_ENGINE_MAXIMUM_CLIMB_RATE_METERS_PER_SECOND=3
VIMANTRA_VALIDATION_ENGINE_MAXIMUM_DESCENT_RATE_METERS_PER_SECOND=3
VIMANTRA_VALIDATION_ENGINE_MINIMUM_SPEED_METERS_PER_SECOND=1
VIMANTRA_VALIDATION_ENGINE_CRUISE_SPEED_METERS_PER_SECOND=12
VIMANTRA_VALIDATION_ENGINE_MAXIMUM_SPEED_METERS_PER_SECOND=15
VIMANTRA_VALIDATION_ENGINE_MAXIMUM_MISSION_DISTANCE_METERS=5000
VIMANTRA_VALIDATION_ENGINE_MAXIMUM_SINGLE_LEG_DISTANCE_METERS=2000
VIMANTRA_VALIDATION_ENGINE_MINIMUM_WAYPOINT_SPACING_METERS=2
VIMANTRA_VALIDATION_ENGINE_MAXIMUM_FLIGHT_TIME_SECONDS=900
VIMANTRA_VALIDATION_ENGINE_MAXIMUM_BATTERY_USAGE_PERCENT=75
VIMANTRA_VALIDATION_ENGINE_MINIMUM_BATTERY_RESERVE_PERCENT=25
VIMANTRA_VALIDATION_ENGINE_SHARP_TURN_WARNING_DEGREES=110
VIMANTRA_VALIDATION_ENGINE_SHARP_TURN_ERROR_DEGREES=145
```

Invalid combinations fail during application startup.

## API

```http
GET /missions/{mission_id}/validation
```

The endpoint returns the standard API envelope with `MissionValidationResponse`
in `data`.

```json
{
  "status": "warning",
  "score": 85,
  "errors": [],
  "warnings": [
    {
      "code": "CRUISE_SPEED_HIGH",
      "message": "Waypoint speed is above the recommended cruise speed.",
      "category": "Speed",
      "waypoint": 2
    }
  ],
  "checks": [],
  "summary": {
    "errors": 0,
    "warnings": 1,
    "passed": true,
    "passed_checks": 12,
    "failed_checks": 0
  }
}
```

## Frontend

The Mission Validation panel appears separately from Mission Analytics after a
mission is saved or loaded. It displays mission readiness, score, errors,
warnings, passed checks, failed checks, and expandable rule categories.

## Screenshots

Screenshots should be captured from the running application after deployment,
because the panel reflects live mission data and configured thresholds.
