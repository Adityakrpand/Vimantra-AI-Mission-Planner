from __future__ import annotations

from datetime import datetime, timezone

from app.models.mission import MissionRecord, Waypoint
from validation.config import ValidationEngineConfig
from validation.rules import estimated_battery_usage_percent, leg_distances_meters
from validation.validator import MissionValidationEngine


def test_valid_mission_is_ready() -> None:
    result = service().validate(mission())

    assert result.status == "ready"
    assert result.score == 100
    assert result.summary.passed is True
    assert result.errors == []


def test_invalid_altitude_fails() -> None:
    result = service().validate(
        mission(waypoints=[point(1, altitude=80), point(2, altitude=200)])
    )

    assert "ALTITUDE_TOO_HIGH" in error_codes(result)
    assert result.summary.passed is False


def test_invalid_battery_reserve_fails() -> None:
    result = service(
        config(minimum_battery_reserve_percent=99, maximum_battery_usage_percent=1)
    ).validate(mission())

    assert {"BATTERY_USAGE_TOO_HIGH", "LOW_BATTERY_RESERVE"} <= error_codes(result)


def test_invalid_speed_fails() -> None:
    result = service().validate(
        mission(waypoints=[point(1, speed=8), point(2, speed=25)])
    )

    assert "SPEED_TOO_HIGH" in error_codes(result)


def test_duplicate_consecutive_waypoints_fail() -> None:
    result = service().validate(
        mission(
            waypoints=[
                point(1, latitude=19.076, longitude=72.8777),
                point(2, latitude=19.076, longitude=72.8777),
            ]
        )
    )

    assert {"DUPLICATE_WAYPOINT", "MINIMUM_WAYPOINT_DISTANCE"} <= error_codes(result)


def test_empty_mission_fails() -> None:
    result = service().validate(mission(waypoints=[]))

    assert {"EMPTY_MISSION", "INVALID_PATH"} <= error_codes(result)


def test_maximum_distance_fails() -> None:
    result = service(config(maximum_mission_distance_meters=100)).validate(mission())

    assert "MAXIMUM_MISSION_DISTANCE" in error_codes(result)


def test_invalid_coordinates_fail() -> None:
    result = service().validate(
        mission(
            waypoints=[
                raw_point(1, latitude=91, longitude=72.8777),
                raw_point(2, latitude=19.0821, longitude=181),
            ]
        )
    )

    assert {"INVALID_LATITUDE", "INVALID_LONGITUDE"} <= error_codes(result)


def test_edge_cases_cover_time_climb_descent_and_sharp_turns() -> None:
    sample = mission(
        waypoints=[
            point(1, latitude=19.0, longitude=72.0, altitude=20, speed=15),
            point(2, latitude=19.0, longitude=72.01, altitude=120, speed=15),
            point(3, latitude=19.0, longitude=72.0, altitude=20, speed=15),
        ]
    )

    result = service(
        config(
            maximum_altitude_jump_meters=20,
            maximum_climb_rate_meters_per_second=0.1,
            maximum_descent_rate_meters_per_second=0.1,
            maximum_flight_time_seconds=1,
        )
    ).validate(sample)

    assert {
        "SUDDEN_ALTITUDE_JUMP",
        "CLIMB_RATE_TOO_HIGH",
        "DESCENT_RATE_TOO_HIGH",
        "MAXIMUM_FLIGHT_TIME",
        "EXTREMELY_SHARP_TURN",
    } <= error_and_warning_codes(result)


def test_validation_helpers_are_deterministic() -> None:
    sample = mission()

    assert leg_distances_meters(sample.waypoints) == leg_distances_meters(
        sample.waypoints
    )
    assert estimated_battery_usage_percent(2000, 50, 4) == 9.5


def service(
    engine_config: ValidationEngineConfig | None = None,
) -> MissionValidationEngine:
    return MissionValidationEngine(engine_config or config())


def config(**overrides: object) -> ValidationEngineConfig:
    values = {
        "minimum_waypoints": 2,
        "maximum_waypoints": 100,
        "minimum_altitude_meters": 5.0,
        "maximum_altitude_meters": 120.0,
        "maximum_altitude_jump_meters": 60.0,
        "maximum_climb_rate_meters_per_second": 3.0,
        "maximum_descent_rate_meters_per_second": 3.0,
        "minimum_speed_meters_per_second": 1.0,
        "cruise_speed_meters_per_second": 12.0,
        "maximum_speed_meters_per_second": 15.0,
        "maximum_mission_distance_meters": 5000.0,
        "maximum_single_leg_distance_meters": 2000.0,
        "minimum_waypoint_spacing_meters": 2.0,
        "maximum_flight_time_seconds": 900.0,
        "maximum_battery_usage_percent": 75.0,
        "minimum_battery_reserve_percent": 25.0,
        "sharp_turn_warning_degrees": 110.0,
        "sharp_turn_error_degrees": 145.0,
    }
    values.update(overrides)
    return ValidationEngineConfig(**values)


def mission(waypoints: list[Waypoint] | None = None) -> MissionRecord:
    return MissionRecord(
        id=1,
        name="Validation Mission",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        waypoints=waypoints
        if waypoints is not None
        else [
            point(1, latitude=19.076, longitude=72.8777),
            point(2, latitude=19.0821, longitude=72.8903),
        ],
    )


def point(
    sequence: int,
    *,
    latitude: float = 19.076,
    longitude: float = 72.8777,
    altitude: float = 80,
    speed: float = 8,
) -> Waypoint:
    return Waypoint(
        sequence=sequence,
        latitude=latitude,
        longitude=longitude,
        altitude_meters=altitude,
        speed_meters_per_second=speed,
    )


def raw_point(
    sequence: int,
    *,
    latitude: float,
    longitude: float,
) -> Waypoint:
    return Waypoint.model_construct(
        sequence=sequence,
        latitude=latitude,
        longitude=longitude,
        altitude_meters=80,
        speed_meters_per_second=8,
    )


def error_codes(result) -> set[str]:
    return {issue.code for issue in result.errors}


def error_and_warning_codes(result) -> set[str]:
    return {issue.code for issue in result.errors + result.warnings}
