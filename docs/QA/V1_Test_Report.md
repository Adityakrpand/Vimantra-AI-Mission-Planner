# V1 End-to-End QA Test Report

Date: 2026-07-07

## Summary

Vimantra AI Mission Planner was tested as a finished V1 release candidate with
live backend, live frontend, browser inspection, API edge cases, stress mission
payloads, validation, analytics, and regression suites.

Result: no critical release-blocking bugs remain after fixes in this QA pass.

## Environment

- OS: Windows
- Frontend: Vite dev server at `http://127.0.0.1:5173`
- Backend: FastAPI/Uvicorn at `http://127.0.0.1:8000`
- Backend health: `200 OK`
- Browser: in-app browser, desktop/tablet/mobile viewport checks
- PX4 SITL: not connected during this QA pass

## Passed Tests

### Mission Creation

- Empty mission rejected with `422 VALIDATION_ERROR`.
- Invalid coordinate mission rejected with `422 VALIDATION_ERROR`.
- Single waypoint mission saved successfully when sent as a valid JSON array.
- Two waypoint mission saved, loaded, analyzed, and validated.
- 10 waypoint mission saved, loaded, analyzed, and validated.
- 100 waypoint mission saved, loaded, analyzed, and validated.
- 250 waypoint mission saved, loaded, analyzed, and validated.
- 500 waypoint mission saved, loaded, analyzed, and validated.
- 1000 waypoint mission saved, loaded, analyzed, and validated.
- Duplicate waypoint mission saved and correctly reported validation issues.
- Special-character mission name saved successfully.

### Waypoint Editing

- Waypoint insertion through `Add WP` works.
- Delete buttons render for waypoints.
- Altitude edits persist in the UI and saved mission.
- Speed edits persist in the UI and saved mission.
- Frontend numeric bounds clamp excessive values instead of crashing.
- Reloading and loading a saved mission restores waypoint values.

Not available in V1: drag-to-move, arbitrary insert-between, and undo controls.
These were not treated as bugs because the UI does not expose those features.

### Save And Load

- Save mission works.
- Load mission works after browser reload.
- Duplicate names are allowed and load correctly.
- Long/special names are accepted up to configured model limits.
- Large missions save and load through the API.

### Validation

- `GET /missions/{mission_id}/validation` returns structured readiness data.
- Single waypoint mission returns `MINIMUM_WAYPOINTS` and `INVALID_PATH`.
- Duplicate waypoints return `DUPLICATE_WAYPOINT` and `MINIMUM_WAYPOINT_DISTANCE`.
- High cruise speed returns warning state and score reduction.
- Validation dashboard renders after loading a saved mission.
- Upload is blocked by pre-flight when the drone is disconnected.

### Analytics

- `GET /missions/{mission_id}/analytics` returns deterministic summary and statistics.
- Distance, estimated flight time, battery usage, battery remaining, speed, altitude,
  climb/descent, turns, longest leg, and shortest leg endpoints respond successfully.
- Analytics panel renders after loading a saved mission.

### API

- `GET /health`: `200`.
- `POST /missions`: `201` for valid payloads.
- `POST /missions`: `422` for empty, invalid, and malformed payloads.
- `GET /missions/{missing_id}`: `404 NOT_FOUND`.
- `POST /missions/{missing_id}/upload`: `404 NOT_FOUND`.
- `POST /missions/{id}/upload` while disconnected: structured `PREFLIGHT_FAILED`.
- All checked API errors used the standardized response envelope.

### UI

- Application loads at `http://127.0.0.1:5173`.
- Browser console had no errors or warnings during live checks.
- Mission list, mission planner, map, drone status, and command bar render.
- Validation and Analytics panels show consistent loading/empty/unavailable states.
- Responsive layout works at desktop, tablet, and mobile widths after the fix below.

## Performance Observations

Measured with local FastAPI and SQLite on Windows.

| Scenario | Save | Load | Analytics | Validation |
| --- | ---: | ---: | ---: | ---: |
| 2 waypoints | 62 ms | 68 ms | 42 ms | 32 ms |
| 10 waypoints | 99 ms | 48 ms | 33 ms | 43 ms |
| 100 waypoints | 70 ms | 42 ms | 21 ms | 32 ms |
| 250 waypoints | 87 ms | 34 ms | 25 ms | 28 ms |
| 500 waypoints | 159 ms | 140 ms | 78 ms | 35 ms |
| 1000 waypoints | 358 ms | 122 ms | 43 ms | 59 ms |

The API remains responsive for 1000-waypoint payloads in local testing.

## Issues Found And Fixed

### Fixed: Stale Backend During QA

Symptom: `/missions/{id}/validation` returned a generic `404`.

Cause: the running backend process was started before Sprint 17 and did not
include the validation dashboard route.

Resolution: restarted backend from `scripts/start_backend.ps1`. Latest backend
returned `200` validation responses.

### Fixed: Responsive Horizontal Overflow

Symptom: tablet and mobile viewport checks showed horizontal overflow because
the app used a fixed three-column grid with a minimum width around `1022px`.

Resolution: updated the frontend shell to stack panels below the `lg` breakpoint,
wrap command buttons, and give the map a stable stacked height.

Verification:

- Desktop `1280x720`: no horizontal overflow.
- Tablet `900x700`: no horizontal overflow.
- Mobile `390x844`: no horizontal overflow.
- Frontend tests passed.
- Frontend build passed.

## Minor Issues / Notes

- Backend tests still show FastAPI `on_event` deprecation warnings. This is not
  release-blocking, but should be addressed in a future framework maintenance sprint.
- Mission list can contain many duplicate names from stress/QA testing. The list
  remains scrollable, but production seed/test data should be kept clean before
  public demos.
- PX4 SITL was not connected, so real vehicle connection/arming/start was not
  verified in this pass. Disconnected-state handling was verified.

## Regression Verification

- Backend tests: `108 passed`.
- Frontend tests: `15 passed`.
- Frontend production build: passed.
- Browser console: no errors or warnings observed.
- Backend error log: no unexpected exceptions observed.

## Recommendations

- Run one final PX4 SITL connected workflow before tagging the public release.
- Consider migrating FastAPI shutdown handling from `on_event` to lifespan in a
  future maintenance sprint.
- Keep release/demo databases clean or provide a reset script for demo data.
- Consider virtualizing very large waypoint lists in a future performance sprint
  if 1000+ waypoint missions become common in the UI.
