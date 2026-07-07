# Logging

Sprint 13 adds a centralized backend logging subsystem and a lightweight frontend development logger.

## Architecture

Backend logging lives in `backend/logging/` and is configured once during FastAPI startup. Application code uses `get_logger(__name__)` and audit helpers instead of direct `print()` statements or one-off logger setup.

Core pieces:

- `logger.py`: single logging configuration entry point.
- `formatter.py`: structured readable log format.
- `handlers.py`: console, rotating file, and daily file handlers.
- `context.py`: request, mission, and future drone context.
- `filters.py`: injects context into every record.
- `audit.py`: typed audit event writer.
- `constants.py`: logger names and audit event names.

The frontend utility lives at `frontend/src/services/logger.ts`. It only writes to the browser console in development mode.

## Log Locations

Defaults:

- `logs/vimantra.log`: size-based rotating application log.
- `logs/vimantra-daily.log`: daily rotating application log.

Change the directory with:

```text
VIMANTRA_LOG_DIRECTORY=logs
```

Production deployments should use an absolute log directory such as `/var/log/vimantra` or a mounted platform log path.

## Log Format

Each backend log line includes:

- ISO-8601 UTC timestamp.
- Log level.
- Module name.
- Function name.
- Request ID when available.
- Mission ID when available.
- Drone ID placeholder for future hardware identity.
- Message.
- Exception stack trace when applicable.

Example:

```text
2026-07-07T14:20:55Z INFO mission_upload upload_mission request_id=abc123 mission_id=42 drone_id=- Mission uploaded waypoint_count=5
```

## Log Levels

Set the level through configuration:

```text
VIMANTRA_LOG_LEVEL=INFO
```

Supported values:

- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

For local diagnostics:

```powershell
$env:VIMANTRA_LOG_LEVEL = "DEBUG"
.\scripts\start_backend.ps1
```

## Audit Events

Audit logs record important operational events without exposing sensitive values:

- Application startup and shutdown.
- Configuration loaded and configuration validation failure.
- Mission created, loaded, deleted, validated, uploaded, and upload failed.
- Pre-flight checks executed.
- Drone connected and disconnected.
- Vehicle armed and disarmed.
- Mission started.
- Telemetry timeout.
- Unhandled exceptions.

Reserved event names also exist for mission update, pause, resume, completion, and return-to-home workflows when those features are implemented.

## Troubleshooting

If logs do not appear:

- Confirm `VIMANTRA_LOG_FILE_ENABLED=true`.
- Confirm `VIMANTRA_LOG_DIRECTORY` points to a writable directory.
- Confirm `VIMANTRA_LOG_LEVEL` is not filtering the event.
- Use `VIMANTRA_LOG_CONSOLE_ENABLED=true` while debugging startup issues.

If startup fails after changing logging settings:

- `VIMANTRA_LOG_LEVEL` must be one of the supported uppercase names.
- `VIMANTRA_LOG_MAX_FILE_SIZE_BYTES` must be greater than zero.
- `VIMANTRA_LOG_RETENTION_DAYS` must be greater than zero.
- `VIMANTRA_LOG_DIRECTORY` cannot be empty.
