from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from config import defaults
from config.environment import RuntimeEnvironment
from config.validation import (
    validate_environment,
    validate_less_than,
    validate_not_empty_path,
    validate_positive,
)
from mission.validation_rules import MissionValidationConfig


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        env_prefix="VIMANTRA_",
        extra="ignore",
    )

    env: RuntimeEnvironment = Field(default=RuntimeEnvironment.DEVELOPMENT)
    debug: bool = Field(default=defaults.DEFAULT_DEBUG)
    log_level: str = Field(default=defaults.DEFAULT_LOG_LEVEL)
    log_directory: Path = Field(default=Path(defaults.DEFAULT_LOG_DIRECTORY))
    log_max_file_size_bytes: int = Field(
        default=defaults.DEFAULT_LOG_MAX_FILE_SIZE_BYTES
    )
    log_retention_days: int = Field(default=defaults.DEFAULT_LOG_RETENTION_DAYS)
    log_console_enabled: bool = Field(default=defaults.DEFAULT_LOG_CONSOLE_ENABLED)
    log_file_enabled: bool = Field(default=defaults.DEFAULT_LOG_FILE_ENABLED)
    api_host: str = Field(default=defaults.DEFAULT_API_HOST)
    api_port: int = Field(default=defaults.DEFAULT_API_PORT)
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: list(defaults.DEFAULT_CORS_ORIGINS)
    )

    database_path: Path = Field(default=Path(defaults.DEFAULT_DATABASE_PATH))

    mavsdk_address: str = Field(default=defaults.DEFAULT_MAVSDK_ADDRESS)
    drone_connection_timeout_seconds: float = Field(
        default=defaults.DEFAULT_DRONE_CONNECTION_TIMEOUT_SECONDS
    )
    telemetry_refresh_interval_seconds: float = Field(
        default=defaults.DEFAULT_TELEMETRY_REFRESH_INTERVAL_SECONDS
    )
    telemetry_read_timeout_seconds: float = Field(
        default=defaults.DEFAULT_TELEMETRY_READ_TIMEOUT_SECONDS
    )
    mission_upload_timeout_seconds: float = Field(
        default=defaults.DEFAULT_MISSION_UPLOAD_TIMEOUT_SECONDS
    )
    mission_timeout_seconds: float = Field(default=defaults.DEFAULT_MISSION_TIMEOUT_SECONDS)

    validation_minimum_waypoints: int = Field(
        default=defaults.DEFAULT_VALIDATION_MINIMUM_WAYPOINTS
    )
    validation_maximum_waypoints: int = Field(
        default=defaults.DEFAULT_VALIDATION_MAXIMUM_WAYPOINTS
    )
    validation_minimum_altitude_meters: float = Field(
        default=defaults.DEFAULT_VALIDATION_MINIMUM_ALTITUDE_METERS
    )
    validation_maximum_altitude_meters: float = Field(
        default=defaults.DEFAULT_VALIDATION_MAXIMUM_ALTITUDE_METERS
    )
    validation_minimum_speed_meters_per_second: float = Field(
        default=defaults.DEFAULT_VALIDATION_MINIMUM_SPEED_METERS_PER_SECOND
    )
    validation_maximum_speed_meters_per_second: float = Field(
        default=defaults.DEFAULT_VALIDATION_MAXIMUM_SPEED_METERS_PER_SECOND
    )
    validation_high_speed_warning_meters_per_second: float = Field(
        default=defaults.DEFAULT_VALIDATION_HIGH_SPEED_WARNING_METERS_PER_SECOND
    )
    validation_distance_warning_meters: float = Field(
        default=defaults.DEFAULT_VALIDATION_DISTANCE_WARNING_METERS
    )
    validation_close_waypoint_warning_meters: float = Field(
        default=defaults.DEFAULT_VALIDATION_CLOSE_WAYPOINT_WARNING_METERS
    )

    @field_validator("env", mode="before")
    @classmethod
    def _validate_env(cls, value: Any) -> RuntimeEnvironment:
        if isinstance(value, RuntimeEnvironment):
            return value

        return validate_environment(str(value))

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]

        return value

    @field_validator("log_level", mode="before")
    @classmethod
    def _validate_log_level(cls, value: Any) -> str:
        normalized = str(value).upper()
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if normalized not in valid_levels:
            raise ValueError(
                "VIMANTRA_LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, or CRITICAL."
            )

        return normalized

    @field_validator("database_path", mode="before")
    @classmethod
    def _validate_database_path_input(cls, value: Any) -> Any:
        if isinstance(value, str) and value.strip() == "":
            raise ValueError("VIMANTRA_DATABASE_PATH cannot be empty.")

        return value

    @field_validator("log_directory", mode="before")
    @classmethod
    def _validate_log_directory_input(cls, value: Any) -> Any:
        if isinstance(value, str) and value.strip() == "":
            raise ValueError("VIMANTRA_LOG_DIRECTORY cannot be empty.")

        return value

    @model_validator(mode="after")
    def _validate_settings(self) -> AppSettings:
        validate_not_empty_path(self.database_path, "VIMANTRA_DATABASE_PATH")
        validate_not_empty_path(self.log_directory, "VIMANTRA_LOG_DIRECTORY")
        if self.api_port <= 0:
            raise ValueError("VIMANTRA_API_PORT must be greater than zero.")
        if self.log_max_file_size_bytes <= 0:
            raise ValueError("VIMANTRA_LOG_MAX_FILE_SIZE_BYTES must be greater than zero.")
        if self.log_retention_days <= 0:
            raise ValueError("VIMANTRA_LOG_RETENTION_DAYS must be greater than zero.")
        validate_positive(
            self.drone_connection_timeout_seconds,
            "VIMANTRA_DRONE_CONNECTION_TIMEOUT_SECONDS",
        )
        validate_positive(
            self.telemetry_refresh_interval_seconds,
            "VIMANTRA_TELEMETRY_REFRESH_INTERVAL_SECONDS",
        )
        validate_positive(
            self.telemetry_read_timeout_seconds,
            "VIMANTRA_TELEMETRY_READ_TIMEOUT_SECONDS",
        )
        validate_positive(
            self.mission_upload_timeout_seconds,
            "VIMANTRA_MISSION_UPLOAD_TIMEOUT_SECONDS",
        )
        validate_positive(self.mission_timeout_seconds, "VIMANTRA_MISSION_TIMEOUT_SECONDS")
        validate_positive(
            self.validation_minimum_speed_meters_per_second,
            "VIMANTRA_VALIDATION_MINIMUM_SPEED_METERS_PER_SECOND",
        )
        if self.validation_minimum_waypoints <= 0:
            raise ValueError(
                "VIMANTRA_VALIDATION_MINIMUM_WAYPOINTS must be greater than zero."
            )
        if self.validation_maximum_waypoints <= 0:
            raise ValueError(
                "VIMANTRA_VALIDATION_MAXIMUM_WAYPOINTS must be greater than zero."
            )
        validate_positive(
            self.validation_maximum_speed_meters_per_second,
            "VIMANTRA_VALIDATION_MAXIMUM_SPEED_METERS_PER_SECOND",
        )
        validate_less_than(
            self.validation_minimum_altitude_meters,
            self.validation_maximum_altitude_meters,
            "VIMANTRA_VALIDATION_MINIMUM_ALTITUDE_METERS",
            "VIMANTRA_VALIDATION_MAXIMUM_ALTITUDE_METERS",
        )
        validate_less_than(
            self.validation_minimum_speed_meters_per_second,
            self.validation_maximum_speed_meters_per_second,
            "VIMANTRA_VALIDATION_MINIMUM_SPEED_METERS_PER_SECOND",
            "VIMANTRA_VALIDATION_MAXIMUM_SPEED_METERS_PER_SECOND",
        )
        if self.validation_maximum_waypoints < self.validation_minimum_waypoints:
            raise ValueError(
                "VIMANTRA_VALIDATION_MAXIMUM_WAYPOINTS must be greater than or "
                "equal to VIMANTRA_VALIDATION_MINIMUM_WAYPOINTS."
            )

        return self

    @property
    def resolved_database_path(self) -> Path:
        if self.database_path.is_absolute():
            return self.database_path

        return repository_root() / self.database_path

    @property
    def resolved_log_directory(self) -> Path:
        if self.log_directory.is_absolute():
            return self.log_directory

        return repository_root() / self.log_directory

    def mission_validation_config(self) -> MissionValidationConfig:
        return MissionValidationConfig(
            minimum_waypoints=self.validation_minimum_waypoints,
            maximum_waypoints=self.validation_maximum_waypoints,
            minimum_altitude_meters=self.validation_minimum_altitude_meters,
            maximum_altitude_meters=self.validation_maximum_altitude_meters,
            minimum_speed_meters_per_second=self.validation_minimum_speed_meters_per_second,
            maximum_speed_meters_per_second=self.validation_maximum_speed_meters_per_second,
            high_speed_warning_meters_per_second=(
                self.validation_high_speed_warning_meters_per_second
            ),
            maximum_distance_warning_meters=self.validation_distance_warning_meters,
            close_waypoint_warning_meters=self.validation_close_waypoint_warning_meters,
        )


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings(_env_file=_environment_files())


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _environment_files() -> tuple[Path, ...]:
    root = repository_root()
    env_name = os.environ.get("VIMANTRA_ENV", defaults.DEFAULT_ENVIRONMENT)
    return (
        root / ".env",
        root / f".env.{env_name}",
    )
