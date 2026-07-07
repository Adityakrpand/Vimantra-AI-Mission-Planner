from __future__ import annotations

from enum import StrEnum

LOGGER_NAME = "vimantra"
AUDIT_LOGGER_NAME = f"{LOGGER_NAME}.audit"
REQUEST_ID_KEY = "request_id"
MISSION_ID_KEY = "mission_id"
DRONE_ID_KEY = "drone_id"
MISSING_CONTEXT_VALUE = "-"


class AuditEvent(StrEnum):
    APPLICATION_STARTUP = "application_startup"
    APPLICATION_SHUTDOWN = "application_shutdown"
    CONFIGURATION_LOADED = "configuration_loaded"
    CONFIGURATION_VALIDATION_FAILED = "configuration_validation_failed"
    DRONE_CONNECTED = "drone_connected"
    DRONE_DISCONNECTED = "drone_disconnected"
    MISSION_COMPLETED = "mission_completed"
    MISSION_CREATED = "mission_created"
    MISSION_DELETED = "mission_deleted"
    MISSION_LOADED = "mission_loaded"
    MISSION_PAUSED = "mission_paused"
    MISSION_RESUMED = "mission_resumed"
    MISSION_STARTED = "mission_started"
    MISSION_UPDATED = "mission_updated"
    MISSION_UPLOADED = "mission_uploaded"
    MISSION_UPLOAD_FAILED = "mission_upload_failed"
    MISSION_VALIDATED = "mission_validated"
    PREFLIGHT_EXECUTED = "preflight_executed"
    RETURN_TO_HOME_INITIATED = "return_to_home_initiated"
    TELEMETRY_TIMEOUT = "telemetry_timeout"
    UNHANDLED_EXCEPTION = "unhandled_exception"
    VEHICLE_ARMED = "vehicle_armed"
    VEHICLE_DISARMED = "vehicle_disarmed"
