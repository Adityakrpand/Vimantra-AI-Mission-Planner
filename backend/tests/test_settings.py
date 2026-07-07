from pathlib import Path

import pytest
from pydantic import ValidationError

from config.environment import RuntimeEnvironment
from config.settings import AppSettings
from mission.validation_models import MissionValidationRequest, MissionValidationWaypoint
from mission.validator import MissionValidator


def test_settings_load_default_values() -> None:
    settings = AppSettings(_env_file=None)

    assert settings.env == RuntimeEnvironment.DEVELOPMENT
    assert settings.debug is True
    assert settings.log_level == "INFO"
    assert settings.log_directory == Path("logs")
    assert settings.log_file_enabled is True
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 8000
    assert settings.mavsdk_address == "udp://:14540"
    assert settings.mission_validation_config().minimum_altitude_meters == 5
    assert settings.preflight_config().battery_warning_threshold_percent == 30
    assert settings.preflight_config().gps_minimum_satellites == 6
    assert settings.preflight_config().optional_checks_enabled is True
    assert settings.mission_analytics_config().maximum_recommended_distance_meters == 5000
    assert settings.mission_analytics_config().battery_warning_threshold_percent == 25
    assert settings.validation_engine_config().maximum_mission_distance_meters == 5000
    assert settings.validation_engine_config().minimum_battery_reserve_percent == 25


def test_settings_load_environment_overrides(tmp_path: Path) -> None:
    env_file = tmp_path / ".env.testing"
    env_file.write_text(
        "\n".join(
            [
                "VIMANTRA_ENV=testing",
                "VIMANTRA_DEBUG=false",
                "VIMANTRA_LOG_LEVEL=DEBUG",
                "VIMANTRA_LOG_DIRECTORY=logs/testing",
                "VIMANTRA_LOG_FILE_ENABLED=false",
                "VIMANTRA_API_PORT=9000",
                "VIMANTRA_DATABASE_PATH=database/test.sqlite",
                "VIMANTRA_MAVSDK_ADDRESS=udp://:14541",
                "VIMANTRA_VALIDATION_MINIMUM_ALTITUDE_METERS=10",
                "VIMANTRA_PREFLIGHT_BATTERY_WARNING_THRESHOLD_PERCENT=40",
                "VIMANTRA_PREFLIGHT_GPS_MINIMUM_SATELLITES=8",
                "VIMANTRA_PREFLIGHT_OPTIONAL_CHECKS_ENABLED=false",
                "VIMANTRA_ANALYTICS_MAXIMUM_RECOMMENDED_DISTANCE_METERS=2500",
                "VIMANTRA_ANALYTICS_BATTERY_WARNING_THRESHOLD_PERCENT=35",
                "VIMANTRA_ANALYTICS_AVERAGE_SPEED_WARNING_METERS_PER_SECOND=10",
                "VIMANTRA_ANALYTICS_MAXIMUM_RECOMMENDED_CLIMB_METERS=75",
                "VIMANTRA_ANALYTICS_SHARP_TURN_WARNING_COUNT=3",
                "VIMANTRA_VALIDATION_ENGINE_MAXIMUM_MISSION_DISTANCE_METERS=2400",
                "VIMANTRA_VALIDATION_ENGINE_MINIMUM_BATTERY_RESERVE_PERCENT=35",
                "VIMANTRA_CORS_ORIGINS=http://localhost:3000,http://localhost:5173",
            ]
        ),
        encoding="utf-8",
    )

    settings = AppSettings(_env_file=env_file)

    assert settings.env == RuntimeEnvironment.TESTING
    assert settings.debug is False
    assert settings.log_level == "DEBUG"
    assert settings.log_directory == Path("logs/testing")
    assert settings.log_file_enabled is False
    assert settings.api_port == 9000
    assert settings.database_path == Path("database/test.sqlite")
    assert settings.mavsdk_address == "udp://:14541"
    assert settings.validation_minimum_altitude_meters == 10
    assert settings.preflight_battery_warning_threshold_percent == 40
    assert settings.preflight_gps_minimum_satellites == 8
    assert settings.preflight_optional_checks_enabled is False
    assert settings.analytics_maximum_recommended_distance_meters == 2500
    assert settings.analytics_battery_warning_threshold_percent == 35
    assert settings.analytics_average_speed_warning_meters_per_second == 10
    assert settings.analytics_maximum_recommended_climb_meters == 75
    assert settings.analytics_sharp_turn_warning_count == 3
    assert settings.validation_engine_maximum_mission_distance_meters == 2400
    assert settings.validation_engine_minimum_battery_reserve_percent == 35
    assert settings.cors_origins == ["http://localhost:3000", "http://localhost:5173"]


@pytest.mark.parametrize(
    ("variable", "value"),
    [
        ("VIMANTRA_ENV", "staging"),
        ("VIMANTRA_LOG_LEVEL", "TRACE"),
        ("VIMANTRA_LOG_MAX_FILE_SIZE_BYTES", "0"),
        ("VIMANTRA_LOG_RETENTION_DAYS", "0"),
        ("VIMANTRA_VALIDATION_MINIMUM_ALTITUDE_METERS", "120"),
        ("VIMANTRA_VALIDATION_MINIMUM_SPEED_METERS_PER_SECOND", "0"),
        ("VIMANTRA_DRONE_CONNECTION_TIMEOUT_SECONDS", "0"),
        ("VIMANTRA_DATABASE_PATH", ""),
        ("VIMANTRA_PREFLIGHT_BATTERY_WARNING_THRESHOLD_PERCENT", "101"),
        ("VIMANTRA_PREFLIGHT_GPS_MINIMUM_SATELLITES", "0"),
        ("VIMANTRA_ANALYTICS_MAXIMUM_RECOMMENDED_DISTANCE_METERS", "0"),
        ("VIMANTRA_ANALYTICS_BATTERY_WARNING_THRESHOLD_PERCENT", "101"),
        ("VIMANTRA_ANALYTICS_AVERAGE_SPEED_WARNING_METERS_PER_SECOND", "0"),
        ("VIMANTRA_ANALYTICS_MAXIMUM_RECOMMENDED_CLIMB_METERS", "0"),
        ("VIMANTRA_ANALYTICS_SHARP_TURN_WARNING_COUNT", "-1"),
        ("VIMANTRA_VALIDATION_ENGINE_MINIMUM_WAYPOINTS", "0"),
        ("VIMANTRA_VALIDATION_ENGINE_MAXIMUM_ALTITUDE_METERS", "4"),
        ("VIMANTRA_VALIDATION_ENGINE_MINIMUM_SPEED_METERS_PER_SECOND", "0"),
        ("VIMANTRA_VALIDATION_ENGINE_MAXIMUM_MISSION_DISTANCE_METERS", "0"),
        ("VIMANTRA_VALIDATION_ENGINE_MINIMUM_BATTERY_RESERVE_PERCENT", "101"),
        ("VIMANTRA_VALIDATION_ENGINE_SHARP_TURN_ERROR_DEGREES", "20"),
    ],
)
def test_settings_reject_invalid_configuration(
    tmp_path: Path,
    variable: str,
    value: str,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(f"{variable}={value}", encoding="utf-8")

    with pytest.raises(ValidationError):
        AppSettings(_env_file=env_file)


def test_configured_validation_limits_affect_validator() -> None:
    settings = AppSettings(
        _env_file=None,
        validation_minimum_altitude_meters=20,
        validation_maximum_altitude_meters=120,
    )
    validator = MissionValidator(settings.mission_validation_config())

    result = validator.validate(
        MissionValidationRequest(
            name="Configured Mission",
            waypoints=[
                MissionValidationWaypoint(
                    sequence=1,
                    latitude=19.076,
                    longitude=72.8777,
                    altitude_meters=10,
                    speed_meters_per_second=8,
                ),
                MissionValidationWaypoint(
                    sequence=2,
                    latitude=19.0821,
                    longitude=72.8903,
                    altitude_meters=90,
                    speed_meters_per_second=9,
                ),
            ],
        )
    )

    assert result.valid is False
    assert result.errors[0].code == "ALTITUDE_TOO_LOW"
    assert "20 meters" in result.errors[0].message


def test_settings_resolve_relative_database_path() -> None:
    settings = AppSettings(_env_file=None, database_path=Path("database/custom.sqlite"))

    assert settings.resolved_database_path.is_absolute()
    assert settings.resolved_database_path.name == "custom.sqlite"
