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
- Drone actions that require a connection return `409` when disconnected.
- PX4 connection timeout returns `504`.
- Validation failures return FastAPI validation errors.
