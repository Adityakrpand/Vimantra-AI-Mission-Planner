from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class MissionValidationWaypoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    sequence: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    altitude_meters: float | None = None
    speed_meters_per_second: float | None = None


class MissionValidationRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str | None = None
    waypoints: list[MissionValidationWaypoint] = Field(default_factory=list)


class MissionValidationIssue(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str
    waypoint: int | None = None
    message: str


class MissionValidationStatistics(BaseModel):
    model_config = ConfigDict(frozen=True)

    waypoints: int
    distance: float


class MissionValidationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    valid: bool
    errors: list[MissionValidationIssue]
    warnings: list[MissionValidationIssue]
    statistics: MissionValidationStatistics

