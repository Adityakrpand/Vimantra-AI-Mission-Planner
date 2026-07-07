from __future__ import annotations

from app.models.drone import DroneConnectionStatus, DroneTelemetrySnapshot
from mission.validation_models import MissionValidationResult
from preflight.models import PreFlightCheck, PreFlightConfig
from preflight.status import PreFlightCheckStatus


def mandatory_checks(
    *,
    drone_status: DroneConnectionStatus,
    mission_validation: MissionValidationResult,
    telemetry: DroneTelemetrySnapshot,
    mission_loaded: bool,
    configuration_loaded: bool,
) -> list[PreFlightCheck]:
    return [
        _check(
            "Vehicle Connected",
            drone_status.connected,
            "Vehicle connection is active.",
            "Vehicle is not connected.",
            mandatory=True,
        ),
        _check(
            "Mission Valid",
            mission_validation.valid,
            "Mission validation passed.",
            "Mission validation failed.",
            mandatory=True,
        ),
        _check(
            "GPS Fix Available",
            _has_gps_fix(telemetry),
            "GPS fix is available.",
            "GPS fix is not available.",
            mandatory=True,
        ),
        _check(
            "Battery Available",
            telemetry.battery_percent is not None,
            "Battery telemetry is available.",
            "Battery telemetry is not available.",
            mandatory=True,
        ),
        _check(
            "Telemetry Active",
            _telemetry_active(telemetry),
            "Telemetry is active.",
            "Telemetry is not active.",
            mandatory=True,
        ),
        _check(
            "Flight Controller Reachable",
            drone_status.connected and telemetry.connected,
            "Flight controller is reachable.",
            "Flight controller is not reachable.",
            mandatory=True,
        ),
        _check(
            "Mission Loaded",
            mission_loaded,
            "Mission is loaded for pre-flight.",
            "Mission is not loaded.",
            mandatory=True,
        ),
        _check(
            "Home Position Available",
            telemetry.home_position_available or _has_position(telemetry),
            "Home position is available.",
            "Home position is not available.",
            mandatory=True,
        ),
        _check(
            "Configuration Loaded",
            configuration_loaded,
            "Configuration is loaded.",
            "Configuration is not loaded.",
            mandatory=True,
        ),
    ]


def optional_checks(
    *,
    config: PreFlightConfig,
    mission_validation: MissionValidationResult,
    telemetry: DroneTelemetrySnapshot,
) -> list[PreFlightCheck]:
    if not config.optional_checks_enabled:
        return []

    return [
        _warning_check(
            "Battery Above Warning Threshold",
            telemetry.battery_percent is not None
            and telemetry.battery_percent >= config.battery_warning_threshold_percent,
            "Battery is above warning threshold.",
            "Battery is below warning threshold.",
        ),
        _warning_check(
            "Strong GPS Signal",
            telemetry.gps_satellites is not None
            and telemetry.gps_satellites >= config.gps_minimum_satellites,
            "GPS satellite count is strong.",
            "GPS satellite count is below preferred threshold.",
        ),
        _warning_check(
            "Compass Healthy",
            telemetry.heading_degrees is not None,
            "Compass heading is available.",
            "Compass heading is not available.",
        ),
        _warning_check(
            "Mission Distance Warning",
            not any(
                warning.code == "MISSION_DISTANCE_HIGH"
                for warning in mission_validation.warnings
            ),
            "Mission distance is within warning threshold.",
            "Mission distance exceeds warning threshold.",
        ),
    ]


def _check(
    name: str,
    passed: bool,
    pass_message: str,
    fail_message: str,
    *,
    mandatory: bool,
) -> PreFlightCheck:
    return PreFlightCheck(
        name=name,
        status=PreFlightCheckStatus.PASS if passed else PreFlightCheckStatus.FAIL,
        mandatory=mandatory,
        message=pass_message if passed else fail_message,
    )


def _warning_check(
    name: str,
    passed: bool,
    pass_message: str,
    warning_message: str,
) -> PreFlightCheck:
    return PreFlightCheck(
        name=name,
        status=PreFlightCheckStatus.PASS if passed else PreFlightCheckStatus.WARNING,
        mandatory=False,
        message=pass_message if passed else warning_message,
    )


def _has_gps_fix(telemetry: DroneTelemetrySnapshot) -> bool:
    if telemetry.gps_fix_type is None:
        return False

    return telemetry.gps_fix_type.upper() not in {"NO_FIX", "NONE", "0"}


def _telemetry_active(telemetry: DroneTelemetrySnapshot) -> bool:
    return telemetry.connected and (
        _has_position(telemetry)
        or telemetry.battery_percent is not None
        or telemetry.flight_mode is not None
    )


def _has_position(telemetry: DroneTelemetrySnapshot) -> bool:
    return telemetry.latitude is not None and telemetry.longitude is not None
