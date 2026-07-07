from __future__ import annotations

from pathlib import Path

from config.environment import RuntimeEnvironment


class SettingsValidationError(ValueError):
    pass


def validate_environment(value: str) -> RuntimeEnvironment:
    try:
        return RuntimeEnvironment(value)
    except ValueError as error:
        allowed = ", ".join(environment.value for environment in RuntimeEnvironment)
        raise SettingsValidationError(
            f"VIMANTRA_ENV must be one of: {allowed}."
        ) from error


def validate_positive(value: float, variable_name: str) -> float:
    if value <= 0:
        raise SettingsValidationError(f"{variable_name} must be greater than zero.")

    return value


def validate_less_than(
    minimum: float,
    maximum: float,
    minimum_name: str,
    maximum_name: str,
) -> None:
    if minimum >= maximum:
        raise SettingsValidationError(f"{minimum_name} must be less than {maximum_name}.")


def validate_not_empty_path(value: Path, variable_name: str) -> Path:
    if str(value).strip() == "":
        raise SettingsValidationError(f"{variable_name} cannot be empty.")

    return value

