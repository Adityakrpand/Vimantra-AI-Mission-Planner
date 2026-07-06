from mission.validation_models import MissionValidationRequest, MissionValidationWaypoint
from mission.validator import MissionValidator


def test_validation_fails_with_too_few_waypoints() -> None:
    result = MissionValidator().validate(
        MissionValidationRequest(
            name="Too Short",
            waypoints=[valid_waypoint()],
        )
    )

    assert result.valid is False
    assert_error(result, "TOO_FEW_WAYPOINTS")


def test_validation_fails_with_bad_latitude() -> None:
    result = MissionValidator().validate(
        mission_with_waypoint(valid_waypoint(latitude=91))
    )

    assert result.valid is False
    assert_error(result, "LATITUDE_OUT_OF_RANGE", waypoint=1)


def test_validation_fails_with_bad_longitude() -> None:
    result = MissionValidator().validate(
        mission_with_waypoint(valid_waypoint(longitude=181))
    )

    assert result.valid is False
    assert_error(result, "LONGITUDE_OUT_OF_RANGE", waypoint=1)


def test_validation_fails_with_bad_altitude() -> None:
    low_result = MissionValidator().validate(
        mission_with_waypoint(valid_waypoint(altitude_meters=4))
    )
    high_result = MissionValidator().validate(
        mission_with_waypoint(valid_waypoint(altitude_meters=121))
    )

    assert low_result.valid is False
    assert_error(low_result, "ALTITUDE_TOO_LOW", waypoint=1)
    assert high_result.valid is False
    assert_error(high_result, "ALTITUDE_TOO_HIGH", waypoint=1)


def test_validation_fails_with_bad_speed() -> None:
    low_result = MissionValidator().validate(
        mission_with_waypoint(valid_waypoint(speed_meters_per_second=0.5))
    )
    high_result = MissionValidator().validate(
        mission_with_waypoint(valid_waypoint(speed_meters_per_second=16))
    )

    assert low_result.valid is False
    assert_error(low_result, "SPEED_TOO_LOW", waypoint=1)
    assert high_result.valid is False
    assert_error(high_result, "SPEED_TOO_HIGH", waypoint=1)


def test_validation_fails_with_duplicate_consecutive_waypoint() -> None:
    duplicate = valid_waypoint()
    result = MissionValidator().validate(
        MissionValidationRequest(
            name="Duplicate",
            waypoints=[duplicate, duplicate.model_copy(update={"sequence": 2})],
        )
    )

    assert result.valid is False
    assert_error(result, "DUPLICATE_CONSECUTIVE_WAYPOINT", waypoint=2)
    assert_error(result, "ZERO_DISTANCE_MISSION")


def test_validation_fails_with_missing_mission_name() -> None:
    result = MissionValidator().validate(
        MissionValidationRequest(
            name=" ",
            waypoints=[valid_waypoint(), second_valid_waypoint()],
        )
    )

    assert result.valid is False
    assert_error(result, "MISSION_NAME_REQUIRED")


def test_validation_fails_with_null_waypoint_values() -> None:
    result = MissionValidator().validate(
        MissionValidationRequest(
            name="Null Fields",
            waypoints=[
                MissionValidationWaypoint(sequence=1),
                second_valid_waypoint(),
            ],
        )
    )

    assert result.valid is False
    assert_error(result, "LATITUDE_REQUIRED", waypoint=1)
    assert_error(result, "LONGITUDE_REQUIRED", waypoint=1)
    assert_error(result, "ALTITUDE_METERS_REQUIRED", waypoint=1)
    assert_error(result, "SPEED_METERS_PER_SECOND_REQUIRED", waypoint=1)


def test_validation_succeeds_for_valid_mission() -> None:
    result = MissionValidator().validate(
        MissionValidationRequest(
            name="Valid Mission",
            waypoints=[valid_waypoint(), second_valid_waypoint()],
        )
    )

    assert result.valid is True
    assert result.errors == []
    assert result.statistics.waypoints == 2
    assert result.statistics.distance > 0


def test_validation_handles_100_waypoint_mission() -> None:
    waypoints = [
        MissionValidationWaypoint(
            sequence=index + 1,
            latitude=19.0 + index * 0.0001,
            longitude=72.0 + index * 0.0001,
            altitude_meters=80,
            speed_meters_per_second=8,
        )
        for index in range(100)
    ]

    result = MissionValidator().validate(
        MissionValidationRequest(name="Large Mission", waypoints=waypoints)
    )

    assert result.valid is True
    assert result.statistics.waypoints == 100
    assert result.statistics.distance > 0


def test_validation_returns_warnings_without_blocking() -> None:
    result = MissionValidator().validate(
        MissionValidationRequest(
            name="Warning Mission",
            waypoints=[
                valid_waypoint(speed_meters_per_second=12),
                second_valid_waypoint(),
            ],
        )
    )

    assert result.valid is True
    assert result.errors == []
    assert result.warnings[0].code == "HIGH_SPEED"


def mission_with_waypoint(
    waypoint: MissionValidationWaypoint,
) -> MissionValidationRequest:
    return MissionValidationRequest(
        name="Invalid Mission",
        waypoints=[waypoint, second_valid_waypoint()],
    )


def valid_waypoint(**overrides: float) -> MissionValidationWaypoint:
    return MissionValidationWaypoint(
        sequence=1,
        latitude=overrides.get("latitude", 19.076),
        longitude=overrides.get("longitude", 72.8777),
        altitude_meters=overrides.get("altitude_meters", 80),
        speed_meters_per_second=overrides.get("speed_meters_per_second", 8),
    )


def second_valid_waypoint() -> MissionValidationWaypoint:
    return MissionValidationWaypoint(
        sequence=2,
        latitude=19.0821,
        longitude=72.8903,
        altitude_meters=90,
        speed_meters_per_second=9,
    )


def assert_error(result, code: str, waypoint: int | None = None) -> None:
    assert any(
        error.code == code and (waypoint is None or error.waypoint == waypoint)
        for error in result.errors
    )
