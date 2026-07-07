# Mission Analytics

Sprint 16 adds deterministic mission analytics before upload and flight.

## Scope

Analytics are formula-based and independent from AI, mission validation, and pre-flight checks.

## Metrics

The backend computes total mission distance, estimated flight time, waypoint count, altitude and speed statistics, climb and descent, battery estimates, turn count, and longest and shortest leg distance.

## Warnings

Warnings do not block flight:

- `MISSION_DISTANCE_HIGH`
- `BATTERY_REMAINING_LOW`
- `AVERAGE_SPEED_HIGH`
- `CLIMB_HIGH`
- `SHARP_TURNS_HIGH`

## API

```text
GET /missions/{mission_id}/analytics
```

The response is returned inside the standard API envelope with `summary`, `statistics`, and `warnings`.

## Configuration

```text
VIMANTRA_ANALYTICS_MAXIMUM_RECOMMENDED_DISTANCE_METERS=5000
VIMANTRA_ANALYTICS_BATTERY_WARNING_THRESHOLD_PERCENT=25
VIMANTRA_ANALYTICS_AVERAGE_SPEED_WARNING_METERS_PER_SECOND=12
VIMANTRA_ANALYTICS_MAXIMUM_RECOMMENDED_CLIMB_METERS=100
VIMANTRA_ANALYTICS_SHARP_TURN_WARNING_COUNT=5
```
