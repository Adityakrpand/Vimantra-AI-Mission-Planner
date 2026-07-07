from app.models.drone import DroneConnectionStatus, DroneTelemetrySnapshot
from app.models.mission import MissionRecord, Waypoint
from mission.validation_models import (
    MissionValidationIssue,
    MissionValidationResult,
    MissionValidationStatistics,
)
from preflight.models import PreFlightConfig
from preflight.service import PreFlightService


def test_preflight_fails_when_drone_disconnected() -> None:
    result = service().run(
        mission=mission_record(),
        mission_validation=valid_mission(),
        drone_status=DroneConnectionStatus(
            connected=False,
            system_address=None,
            message="Drone disconnected.",
        ),
        telemetry=good_telemetry(),
        mission_loaded=True,
    )

    assert result.ready is False
    assert _check_status(result, "Vehicle Connected") == "FAIL"


def test_preflight_fails_when_mission_invalid() -> None:
    result = service().run(
        mission=mission_record(),
        mission_validation=invalid_mission(),
        drone_status=connected_status(),
        telemetry=good_telemetry(),
        mission_loaded=True,
    )

    assert result.ready is False
    assert _check_status(result, "Mission Valid") == "FAIL"


def test_preflight_fails_when_telemetry_inactive() -> None:
    result = service().run(
        mission=mission_record(),
        mission_validation=valid_mission(),
        drone_status=connected_status(),
        telemetry=DroneTelemetrySnapshot(
            connected=False,
            message="Telemetry unavailable.",
        ),
        mission_loaded=True,
    )

    assert result.ready is False
    assert _check_status(result, "Telemetry Active") == "FAIL"


def test_preflight_fails_without_gps_fix() -> None:
    telemetry = good_telemetry().model_copy(update={"gps_fix_type": None})

    result = service().run(
        mission=mission_record(),
        mission_validation=valid_mission(),
        drone_status=connected_status(),
        telemetry=telemetry,
        mission_loaded=True,
    )

    assert result.ready is False
    assert _check_status(result, "GPS Fix Available") == "FAIL"


def test_preflight_passes_when_mandatory_checks_pass() -> None:
    result = service().run(
        mission=mission_record(),
        mission_validation=valid_mission(),
        drone_status=connected_status(),
        telemetry=good_telemetry(),
        mission_loaded=True,
    )

    assert result.ready is True
    assert result.score == 100
    assert all(check.status == "PASS" for check in result.checks)


def service() -> PreFlightService:
    return PreFlightService(
        PreFlightConfig(
            battery_warning_threshold_percent=30,
            gps_minimum_satellites=6,
            optional_checks_enabled=True,
        )
    )


def mission_record() -> MissionRecord:
    return MissionRecord(
        id=1,
        name="Preflight Mission",
        created_at="2026-07-07T00:00:00Z",
        updated_at="2026-07-07T00:00:00Z",
        waypoints=[
            Waypoint(
                sequence=1,
                latitude=19.076,
                longitude=72.8777,
                altitude_meters=80,
                speed_meters_per_second=8,
            ),
            Waypoint(
                sequence=2,
                latitude=19.0821,
                longitude=72.8903,
                altitude_meters=90,
                speed_meters_per_second=9,
            ),
        ],
    )


def connected_status() -> DroneConnectionStatus:
    return DroneConnectionStatus(
        connected=True,
        system_address="udp://:14540",
        message="Drone connected.",
    )


def good_telemetry() -> DroneTelemetrySnapshot:
    return DroneTelemetrySnapshot(
        connected=True,
        latitude=19.076,
        longitude=72.8777,
        altitude_meters=80,
        speed_meters_per_second=6,
        heading_degrees=90,
        battery_percent=80,
        gps_satellites=10,
        gps_fix_type="FIX_3D",
        flight_mode="HOLD",
        mission_current=0,
        mission_total=2,
        home_position_available=True,
        message="Telemetry snapshot received.",
    )


def valid_mission() -> MissionValidationResult:
    return MissionValidationResult(
        valid=True,
        errors=[],
        warnings=[],
        statistics=MissionValidationStatistics(waypoints=2, distance=1200),
    )


def invalid_mission() -> MissionValidationResult:
    return MissionValidationResult(
        valid=False,
        errors=[
            MissionValidationIssue(
                code="ALTITUDE_TOO_LOW",
                waypoint=1,
                message="Altitude must be at least 5 meters.",
            )
        ],
        warnings=[],
        statistics=MissionValidationStatistics(waypoints=1, distance=0),
    )


def _check_status(result, name: str) -> str:
    return next(check.status for check in result.checks if check.name == name)
