# Technical Debt And Improvement Register

This register identifies improvement opportunities without changing Version 1.0 behavior.

## Configuration Management

Current state:

- Backend host, port, database path, CORS origins, and MAVSDK defaults are mostly hardcoded for local development.

Recommendation:

- Introduce typed settings for backend configuration.
- Add `.env.example` files for frontend and backend.
- Document environment-specific configuration.

## Logging

Current state:

- Uvicorn logs and operator messages are available, but domain services do not emit structured logs.

Recommendation:

- Add structured logging with request IDs and operation IDs.
- Log mission upload and drone action attempts with safe, non-sensitive metadata.

## API Error Model

Current state:

- FastAPI and route-level HTTP exceptions are used.

Recommendation:

- Standardize error responses with an error code, message, and remediation hint.

## Database Evolution

Current state:

- SQLite schema is applied directly from `schema.sql`.

Recommendation:

- Add a migration tool before introducing schema changes beyond Version 1.0.

## Frontend State Management

Current state:

- The Version 1.0 UI uses local component state.

Recommendation:

- Revisit state organization when adding AI planning, multi-vehicle workflows, or collaboration.

## Telemetry Scaling

Current state:

- Frontend polls telemetry snapshots.

Recommendation:

- Consider WebSocket or Server-Sent Events if telemetry frequency, number of vehicles, or UI complexity grows.

## Safety Review

Current state:

- Version 1.0 is scoped to PX4 SITL.

Recommendation:

- Before physical vehicle operation, define a safety case, command authorization model, operator checklist, and hardware-in-the-loop validation plan.
