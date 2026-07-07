# API Reference

The backend exposes FastAPI-generated OpenAPI documentation at `http://127.0.0.1:8000/docs` when running locally.

All endpoints return the standardized API envelope documented in
[API Response Standard](../04_API/API_Response_Standard.md).

## Health

`GET /health`

Returns backend status and service name.

## Missions

`POST /missions`

Creates a mission with ordered waypoints.

`GET /missions`

Lists saved missions, most recently updated first.

`GET /missions/{mission_id}`

Loads a saved mission by identifier.

`DELETE /missions/{mission_id}`

Deletes a saved mission and its waypoints.

`POST /missions/{mission_id}/upload`

Uploads a saved mission to the connected drone system.

The mission is automatically validated before upload. Invalid missions return `400` with `error.code` set to `MISSION_INVALID` and the structured validation result in `error.details`.

`POST /missions/{mission_id}/preflight`

Runs pre-flight checks for a saved mission. Failed mandatory checks return `ready: false` in the response `data` field when called directly. Upload and start operations return `409` with `error.code` set to `PREFLIGHT_FAILED` when mandatory checks fail.

`GET /missions/{mission_id}/analytics`

Returns deterministic mission analytics, including distance, estimated flight time, battery usage, altitude and speed statistics, turn count, and warnings.

`GET /missions/{mission_id}/validation`

Returns the V1 mission readiness dashboard result for a saved mission. The response includes mission status, score, errors, warnings, passed checks, failed checks, and expandable validation categories. Missing missions return `404` with `error.code` set to `NOT_FOUND`.

## Mission Validation

`POST /api/missions/validate`

Validates a mission without uploading it. The validation result is returned in the response `data` field:

```json
{
  "success": true,
  "request_id": "abc123",
  "data": {
    "valid": false,
    "errors": [
      {
        "code": "ALTITUDE_TOO_LOW",
        "waypoint": 3,
        "message": "Altitude must be at least 5 meters."
      }
    ],
    "warnings": [],
    "statistics": {
      "waypoints": 5,
      "distance": 1280.5
    }
  },
  "error": null
}
```

Warnings do not block upload. Errors block upload.

## Drone

`POST /drone/connect`

Connects to PX4 SITL through MAVSDK.

`POST /drone/disconnect`

Clears the active drone connection.

`GET /drone/status`

Returns current connection state.

`GET /drone/telemetry`

Returns one telemetry snapshot.

`POST /drone/arm`

Arms the connected drone system.

`POST /drone/disarm`

Disarms the connected drone system.

`POST /drone/start-mission`

Starts the uploaded mission.

## Error Principles

- Missing missions return `404`.
- Mission validation failures return `400` with structured validation details.
- Drone actions that require a connection return `409` when disconnected.
- PX4 connection timeout returns `500`.
- Request validation failures return `422`.
- Unhandled exceptions return `500` without exposing stack traces to clients.
