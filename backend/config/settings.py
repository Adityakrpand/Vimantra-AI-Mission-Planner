from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from analytics.models import MissionAnalyticsConfig
from config import defaults
from config.environment import RuntimeEnvironment
from config.validation import (
    validate_environment,
    validate_less_than,
    validate_not_empty_path,
    validate_positive,
)
from mission.validation_rules import MissionValidationConfig
from preflight.models import PreFlightConfig
from validation.config import ValidationEngineConfig


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
    preflight_battery_warning_threshold_percent: float = Field(
        default=defaults.DEFAULT_PREFLIGHT_BATTERY_WARNING_THRESHOLD_PERCENT
    )
    preflight_gps_minimum_satellites: int = Field(
        default=defaults.DEFAULT_PREFLIGHT_GPS_MINIMUM_SATELLITES
    )
    preflight_optional_checks_enabled: bool = Field(
        default=defaults.DEFAULT_PREFLIGHT_OPTIONAL_CHECKS_ENABLED
    )
    analytics_maximum_recommended_distance_meters: float = Field(
        default=defaults.DEFAULT_ANALYTICS_MAXIMUM_RECOMMENDED_DISTANCE_METERS
    )
    analytics_battery_warning_threshold_percent: float = Field(
        default=defaults.DEFAULT_ANALYTICS_BATTERY_WARNING_THRESHOLD_PERCENT
    )
    analytics_average_speed_warning_meters_per_second: float = Field(
        default=defaults.DEFAULT_ANALYTICS_AVERAGE_SPEED_WARNING_METERS_PER_SECOND
    )
    analytics_maximum_recommended_climb_meters: float = Field(
        default=defaults.DEFAULT_ANALYTICS_MAXIMUM_RECOMMENDED_CLIMB_METERS
    )
    analytics_sharp_turn_warning_count: int = Field(
        default=defaults.DEFAULT_ANALYTICS_SHARP_TURN_WARNING_COUNT
    )
    validation_engine_minimum_waypoints: int = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_MINIMUM_WAYPOINTS
    )
    validation_engine_maximum_waypoints: int = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_MAXIMUM_WAYPOINTS
    )
    validation_engine_minimum_altitude_meters: float = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_MINIMUM_ALTITUDE_METERS
    )
    validation_engine_maximum_altitude_meters: float = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_MAXIMUM_ALTITUDE_METERS
    )
    validation_engine_maximum_altitude_jump_meters: float = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_MAXIMUM_ALTITUDE_JUMP_METERS
    )
    validation_engine_maximum_climb_rate_meters_per_second: float = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_MAXIMUM_CLIMB_RATE_METERS_PER_SECOND
    )
    validation_engine_maximum_descent_rate_meters_per_second: float = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_MAXIMUM_DESCENT_RATE_METERS_PER_SECOND
    )
    validation_engine_minimum_speed_meters_per_second: float = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_MINIMUM_SPEED_METERS_PER_SECOND
    )
    validation_engine_cruise_speed_meters_per_second: float = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_CRUISE_SPEED_METERS_PER_SECOND
    )
    validation_engine_maximum_speed_meters_per_second: float = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_MAXIMUM_SPEED_METERS_PER_SECOND
    )
    validation_engine_maximum_mission_distance_meters: float = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_MAXIMUM_MISSION_DISTANCE_METERS
    )
    validation_engine_maximum_single_leg_distance_meters: float = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_MAXIMUM_SINGLE_LEG_DISTANCE_METERS
    )
    validation_engine_minimum_waypoint_spacing_meters: float = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_MINIMUM_WAYPOINT_SPACING_METERS
    )
    validation_engine_maximum_flight_time_seconds: float = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_MAXIMUM_FLIGHT_TIME_SECONDS
    )
    validation_engine_maximum_battery_usage_percent: float = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_MAXIMUM_BATTERY_USAGE_PERCENT
    )
    validation_engine_minimum_battery_reserve_percent: float = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_MINIMUM_BATTERY_RESERVE_PERCENT
    )
    validation_engine_sharp_turn_warning_degrees: float = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_SHARP_TURN_WARNING_DEGREES
    )
    validation_engine_sharp_turn_error_degrees: float = Field(
        default=defaults.DEFAULT_VALIDATION_ENGINE_SHARP_TURN_ERROR_DEGREES
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
        if not 0 <= self.preflight_battery_warning_threshold_percent <= 100:
            raise ValueError(
                "VIMANTRA_PREFLIGHT_BATTERY_WARNING_THRESHOLD_PERCENT must be "
                "between 0 and 100."
            )
        if self.preflight_gps_minimum_satellites <= 0:
            raise ValueError(
                "VIMANTRA_PREFLIGHT_GPS_MINIMUM_SATELLITES must be greater than zero."
            )
        validate_positive(
            self.analytics_maximum_recommended_distance_meters,
            "VIMANTRA_ANALYTICS_MAXIMUM_RECOMMENDED_DISTANCE_METERS",
        )
        if not 0 <= self.analytics_battery_warning_threshold_percent <= 100:
            raise ValueError(
                "VIMANTRA_ANALYTICS_BATTERY_WARNING_THRESHOLD_PERCENT must be "
                "between 0 and 100."
            )
        validate_positive(
            self.analytics_average_speed_warning_meters_per_second,
            "VIMANTRA_ANALYTICS_AVERAGE_SPEED_WARNING_METERS_PER_SECOND",
        )
        validate_positive(
            self.analytics_maximum_recommended_climb_meters,
            "VIMANTRA_ANALYTICS_MAXIMUM_RECOMMENDED_CLIMB_METERS",
        )
        if self.analytics_sharp_turn_warning_count < 0:
            raise ValueError(
                "VIMANTRA_ANALYTICS_SHARP_TURN_WARNING_COUNT cannot be negative."
            )
        self._validate_validation_engine_settings()

        return self

    def _validate_validation_engine_settings(self) -> None:
        if self.validation_engine_minimum_waypoints <= 0:
            raise ValueError(
                "VIMANTRA_VALIDATION_ENGINE_MINIMUM_WAYPOINTS must be greater than zero."
            )
        if (
            self.validation_engine_maximum_waypoints
            < self.validation_engine_minimum_waypoints
        ):
            raise ValueError(
                "VIMANTRA_VALIDATION_ENGINE_MAXIMUM_WAYPOINTS must be greater than "
                "or equal to VIMANTRA_VALIDATION_ENGINE_MINIMUM_WAYPOINTS."
            )
        validate_less_than(
            self.validation_engine_minimum_altitude_meters,
            self.validation_engine_maximum_altitude_meters,
            "VIMANTRA_VALIDATION_ENGINE_MINIMUM_ALTITUDE_METERS",
            "VIMANTRA_VALIDATION_ENGINE_MAXIMUM_ALTITUDE_METERS",
        )
        validate_less_than(
            self.validation_engine_minimum_speed_meters_per_second,
            self.validation_engine_maximum_speed_meters_per_second,
            "VIMANTRA_VALIDATION_ENGINE_MINIMUM_SPEED_METERS_PER_SECOND",
            "VIMANTRA_VALIDATION_ENGINE_MAXIMUM_SPEED_METERS_PER_SECOND",
        )
        numeric_positive_fields = {
            "VIMANTRA_VALIDATION_ENGINE_MAXIMUM_ALTITUDE_JUMP_METERS": (
                self.validation_engine_maximum_altitude_jump_meters
            ),
            "VIMANTRA_VALIDATION_ENGINE_MAXIMUM_CLIMB_RATE_METERS_PER_SECOND": (
                self.validation_engine_maximum_climb_rate_meters_per_second
            ),
            "VIMANTRA_VALIDATION_ENGINE_MAXIMUM_DESCENT_RATE_METERS_PER_SECOND": (
                self.validation_engine_maximum_descent_rate_meters_per_second
            ),
            "VIMANTRA_VALIDATION_ENGINE_MINIMUM_SPEED_METERS_PER_SECOND": (
                self.validation_engine_minimum_speed_meters_per_second
            ),
            "VIMANTRA_VALIDATION_ENGINE_CRUISE_SPEED_METERS_PER_SECOND": (
                self.validation_engine_cruise_speed_meters_per_second
            ),
            "VIMANTRA_VALIDATION_ENGINE_MAXIMUM_SPEED_METERS_PER_SECOND": (
                self.validation_engine_maximum_speed_meters_per_second
            ),
            "VIMANTRA_VALIDATION_ENGINE_MAXIMUM_MISSION_DISTANCE_METERS": (
                self.validation_engine_maximum_mission_distance_meters
            ),
            "VIMANTRA_VALIDATION_ENGINE_MAXIMUM_SINGLE_LEG_DISTANCE_METERS": (
                self.validation_engine_maximum_single_leg_distance_meters
            ),
            "VIMANTRA_VALIDATION_ENGINE_MINIMUM_WAYPOINT_SPACING_METERS": (
                self.validation_engine_minimum_waypoint_spacing_meters
            ),
            "VIMANTRA_VALIDATION_ENGINE_MAXIMUM_FLIGHT_TIME_SECONDS": (
                self.validation_engine_maximum_flight_time_seconds
            ),
        }
        for name, value in numeric_positive_fields.items():
            validate_positive(value, name)
        if not 0 <= self.validation_engine_maximum_battery_usage_percent <= 100:
            raise ValueError(
                "VIMANTRA_VALIDATION_ENGINE_MAXIMUM_BATTERY_USAGE_PERCENT must be "
                "between 0 and 100."
            )
        if not 0 <= self.validation_engine_minimum_battery_reserve_percent <= 100:
            raise ValueError(
                "VIMANTRA_VALIDATION_ENGINE_MINIMUM_BATTERY_RESERVE_PERCENT must be "
                "between 0 and 100."
            )
        if self.validation_engine_sharp_turn_warning_degrees < 0:
            raise ValueError(
                "VIMANTRA_VALIDATION_ENGINE_SHARP_TURN_WARNING_DEGREES cannot be negative."
            )
        if (
            self.validation_engine_sharp_turn_error_degrees
            < self.validation_engine_sharp_turn_warning_degrees
        ):
            raise ValueError(
                "VIMANTRA_VALIDATION_ENGINE_SHARP_TURN_ERROR_DEGREES must be greater "
                "than or equal to VIMANTRA_VALIDATION_ENGINE_SHARP_TURN_WARNING_DEGREES."
            )

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

    def preflight_config(self) -> PreFlightConfig:
        return PreFlightConfig(
            battery_warning_threshold_percent=(
                self.preflight_battery_warning_threshold_percent
            ),
            gps_minimum_satellites=self.preflight_gps_minimum_satellites,
            optional_checks_enabled=self.preflight_optional_checks_enabled,
        )

    def mission_analytics_config(self) -> MissionAnalyticsConfig:
        return MissionAnalyticsConfig(
            maximum_recommended_distance_meters=(
                self.analytics_maximum_recommended_distance_meters
            ),
            battery_warning_threshold_percent=(
                self.analytics_battery_warning_threshold_percent
            ),
            average_speed_warning_meters_per_second=(
                self.analytics_average_speed_warning_meters_per_second
            ),
            maximum_recommended_climb_meters=(
                self.analytics_maximum_recommended_climb_meters
            ),
            sharp_turn_warning_count=self.analytics_sharp_turn_warning_count,
        )

    def validation_engine_config(self) -> ValidationEngineConfig:
        return ValidationEngineConfig(
            minimum_waypoints=self.validation_engine_minimum_waypoints,
            maximum_waypoints=self.validation_engine_maximum_waypoints,
            minimum_altitude_meters=self.validation_engine_minimum_altitude_meters,
            maximum_altitude_meters=self.validation_engine_maximum_altitude_meters,
            maximum_altitude_jump_meters=(
                self.validation_engine_maximum_altitude_jump_meters
            ),
            maximum_climb_rate_meters_per_second=(
                self.validation_engine_maximum_climb_rate_meters_per_second
            ),
            maximum_descent_rate_meters_per_second=(
                self.validation_engine_maximum_descent_rate_meters_per_second
            ),
            minimum_speed_meters_per_second=(
                self.validation_engine_minimum_speed_meters_per_second
            ),
            cruise_speed_meters_per_second=(
                self.validation_engine_cruise_speed_meters_per_second
            ),
            maximum_speed_meters_per_second=(
                self.validation_engine_maximum_speed_meters_per_second
            ),
            maximum_mission_distance_meters=(
                self.validation_engine_maximum_mission_distance_meters
            ),
            maximum_single_leg_distance_meters=(
                self.validation_engine_maximum_single_leg_distance_meters
            ),
            minimum_waypoint_spacing_meters=(
                self.validation_engine_minimum_waypoint_spacing_meters
            ),
            maximum_flight_time_seconds=(
                self.validation_engine_maximum_flight_time_seconds
            ),
            maximum_battery_usage_percent=(
                self.validation_engine_maximum_battery_usage_percent
            ),
            minimum_battery_reserve_percent=(
                self.validation_engine_minimum_battery_reserve_percent
            ),
            sharp_turn_warning_degrees=(
                self.validation_engine_sharp_turn_warning_degrees
            ),
            sharp_turn_error_degrees=self.validation_engine_sharp_turn_error_degrees,
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
