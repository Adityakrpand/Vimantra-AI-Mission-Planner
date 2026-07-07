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
