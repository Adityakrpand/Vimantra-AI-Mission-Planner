from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict

from preflight.status import PreFlightCheckStatus


@dataclass(frozen=True)
class PreFlightConfig:
    battery_warning_threshold_percent: float
    gps_minimum_satellites: int
    optional_checks_enabled: bool


class PreFlightCheck(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    status: PreFlightCheckStatus
    mandatory: bool
    message: str


class PreFlightResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    ready: bool
    score: int
    checks: list[PreFlightCheck]
    warnings: list[PreFlightCheck]
