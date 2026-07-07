# Configuration

Vimantra AI Mission Planner uses environment-driven configuration. Backend settings are typed, validated at startup, and loaded through the backend `config/` package. Frontend runtime configuration is provided through Vite environment variables.

## Configuration Hierarchy

Backend settings are resolved in this order:

1. Built-in defaults that preserve local development behavior.
2. `.env`
3. `.env.<environment>`, where `<environment>` is `development`, `testing`, or `production`.
4. Process environment variables.

Real `.env` files are ignored by Git. Commit only `*.example` files.

## Backend Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `VIMANTRA_ENV` | `development` | Runtime environment |
| `VIMANTRA_DEBUG` | `true` | FastAPI debug mode |
| `VIMANTRA_LOG_LEVEL` | `INFO` | Logging threshold |
| `VIMANTRA_API_HOST` | `127.0.0.1` | API bind host |
| `VIMANTRA_API_PORT` | `8000` | API bind port |
| `VIMANTRA_CORS_ORIGINS` | `http://127.0.0.1:5173,http://localhost:5173` | Allowed browser origins |
| `VIMANTRA_DATABASE_PATH` | `database/missions.sqlite` | SQLite database path |
| `VIMANTRA_MAVSDK_ADDRESS` | `udp://:14540` | Default MAVSDK connection address |
| `VIMANTRA_DRONE_CONNECTION_TIMEOUT_SECONDS` | `10` | PX4 connection timeout |
| `VIMANTRA_TELEMETRY_REFRESH_INTERVAL_SECONDS` | `2` | Frontend telemetry cadence reference |
| `VIMANTRA_TELEMETRY_READ_TIMEOUT_SECONDS` | `1` | Backend telemetry stream read timeout |
| `VIMANTRA_MISSION_UPLOAD_TIMEOUT_SECONDS` | `30` | MAVSDK mission upload timeout |
| `VIMANTRA_MISSION_TIMEOUT_SECONDS` | `60` | Mission operation timeout reserved for future workflow use |
| `VIMANTRA_VALIDATION_MINIMUM_WAYPOINTS` | `2` | Minimum valid mission waypoint count |
| `VIMANTRA_VALIDATION_MAXIMUM_WAYPOINTS` | `100` | Maximum valid mission waypoint count |
| `VIMANTRA_VALIDATION_MINIMUM_ALTITUDE_METERS` | `5` | Minimum allowed waypoint altitude |
| `VIMANTRA_VALIDATION_MAXIMUM_ALTITUDE_METERS` | `120` | Maximum allowed waypoint altitude |
| `VIMANTRA_VALIDATION_MINIMUM_SPEED_METERS_PER_SECOND` | `1` | Minimum allowed waypoint speed |
| `VIMANTRA_VALIDATION_MAXIMUM_SPEED_METERS_PER_SECOND` | `15` | Maximum allowed waypoint speed |
| `VIMANTRA_VALIDATION_HIGH_SPEED_WARNING_METERS_PER_SECOND` | `12` | Warning threshold for high speed |
| `VIMANTRA_VALIDATION_DISTANCE_WARNING_METERS` | `5000` | Warning threshold for long missions |
| `VIMANTRA_VALIDATION_CLOSE_WAYPOINT_WARNING_METERS` | `2` | Warning threshold for close waypoints |
| `VIMANTRA_PREFLIGHT_BATTERY_WARNING_THRESHOLD_PERCENT` | `30` | Optional pre-flight battery warning threshold |
| `VIMANTRA_PREFLIGHT_GPS_MINIMUM_SATELLITES` | `6` | Optional pre-flight strong GPS satellite threshold |
| `VIMANTRA_PREFLIGHT_OPTIONAL_CHECKS_ENABLED` | `true` | Enables optional pre-flight warning checks |
| `VIMANTRA_ANALYTICS_MAXIMUM_RECOMMENDED_DISTANCE_METERS` | `5000` | Analytics warning threshold for mission distance |
| `VIMANTRA_ANALYTICS_BATTERY_WARNING_THRESHOLD_PERCENT` | `25` | Analytics warning threshold for estimated battery remaining |
| `VIMANTRA_ANALYTICS_AVERAGE_SPEED_WARNING_METERS_PER_SECOND` | `12` | Analytics warning threshold for average speed |
| `VIMANTRA_ANALYTICS_MAXIMUM_RECOMMENDED_CLIMB_METERS` | `100` | Analytics warning threshold for total climb |
| `VIMANTRA_ANALYTICS_SHARP_TURN_WARNING_COUNT` | `5` | Analytics warning threshold for sharp turn count |
| `VIMANTRA_VALIDATION_ENGINE_MINIMUM_WAYPOINTS` | `2` | V1 validation minimum waypoint count |
| `VIMANTRA_VALIDATION_ENGINE_MAXIMUM_WAYPOINTS` | `100` | V1 validation maximum waypoint count |
| `VIMANTRA_VALIDATION_ENGINE_MINIMUM_ALTITUDE_METERS` | `5` | V1 validation minimum altitude |
| `VIMANTRA_VALIDATION_ENGINE_MAXIMUM_ALTITUDE_METERS` | `120` | V1 validation maximum altitude |
| `VIMANTRA_VALIDATION_ENGINE_MAXIMUM_ALTITUDE_JUMP_METERS` | `60` | V1 validation sudden altitude jump warning threshold |
| `VIMANTRA_VALIDATION_ENGINE_MAXIMUM_CLIMB_RATE_METERS_PER_SECOND` | `3` | V1 validation maximum safe climb rate |
| `VIMANTRA_VALIDATION_ENGINE_MAXIMUM_DESCENT_RATE_METERS_PER_SECOND` | `3` | V1 validation maximum safe descent rate |
| `VIMANTRA_VALIDATION_ENGINE_MINIMUM_SPEED_METERS_PER_SECOND` | `1` | V1 validation minimum speed |
| `VIMANTRA_VALIDATION_ENGINE_CRUISE_SPEED_METERS_PER_SECOND` | `12` | V1 validation recommended cruise speed |
| `VIMANTRA_VALIDATION_ENGINE_MAXIMUM_SPEED_METERS_PER_SECOND` | `15` | V1 validation maximum speed |
| `VIMANTRA_VALIDATION_ENGINE_MAXIMUM_MISSION_DISTANCE_METERS` | `5000` | V1 validation maximum mission distance |
| `VIMANTRA_VALIDATION_ENGINE_MAXIMUM_SINGLE_LEG_DISTANCE_METERS` | `2000` | V1 validation maximum single-leg distance |
| `VIMANTRA_VALIDATION_ENGINE_MINIMUM_WAYPOINT_SPACING_METERS` | `2` | V1 validation minimum waypoint spacing |
| `VIMANTRA_VALIDATION_ENGINE_MAXIMUM_FLIGHT_TIME_SECONDS` | `900` | V1 validation maximum flight duration |
| `VIMANTRA_VALIDATION_ENGINE_MAXIMUM_BATTERY_USAGE_PERCENT` | `75` | V1 validation maximum estimated battery usage |
| `VIMANTRA_VALIDATION_ENGINE_MINIMUM_BATTERY_RESERVE_PERCENT` | `25` | V1 validation required reserve battery |
| `VIMANTRA_VALIDATION_ENGINE_SHARP_TURN_WARNING_DEGREES` | `110` | V1 validation sharp turn warning threshold |
| `VIMANTRA_VALIDATION_ENGINE_SHARP_TURN_ERROR_DEGREES` | `145` | V1 validation sharp turn error threshold |

## Frontend Variables

| Variable | Purpose |
| --- | --- |
| `VITE_API_BASE_URL` | Backend API base URL used by frontend service clients |

## Startup Sequence

1. FastAPI calls `create_app`.
2. The backend loads `AppSettings`.
3. Settings validation runs.
4. Invalid settings stop startup immediately.
5. Valid settings configure CORS, database path, drone defaults, mission validation, pre-flight checks, mission analytics, telemetry timeout, and upload timeout.

## Best Practices

- Use `.env.development` for local work.
- Use `.env.testing` for isolated test configuration.
- Use `.env.production` only as a local template; provide real production values through deployment secrets or runtime environment variables.
- Do not commit real `.env` files.
- Keep MAVSDK and validation changes environment-specific rather than editing source code.
- Keep pre-flight warning thresholds conservative for real hardware testing.
