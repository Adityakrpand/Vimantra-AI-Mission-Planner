# API Reference

The backend exposes FastAPI-generated OpenAPI documentation at `http://127.0.0.1:8000/docs` when running locally.

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

The mission is automatically validated before upload. Invalid missions return `400` with a structured validation result in the response `detail`.

## Mission Validation

`POST /api/missions/validate`

Validates a mission without uploading it. Returns structured JSON:

```json
{
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
- PX4 connection timeout returns `504`.
- Validation failures return FastAPI validation errors.
