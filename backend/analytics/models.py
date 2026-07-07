from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict


@dataclass(frozen=True)
class MissionAnalyticsConfig:
    maximum_recommended_distance_meters: float
    battery_warning_threshold_percent: float
    average_speed_warning_meters_per_second: float
    maximum_recommended_climb_meters: float
    sharp_turn_warning_count: int


class AnalyticsSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    distance_meters: float
    estimated_flight_time_seconds: float
    estimated_battery_usage_percent: float
    estimated_battery_remaining_percent: float
    waypoint_count: int


class AnalyticsStatistics(BaseModel):
    model_config = ConfigDict(frozen=True)

    maximum_altitude_meters: float
    minimum_altitude_meters: float
    average_altitude_meters: float
    average_speed_meters_per_second: float
    maximum_speed_meters_per_second: float
    total_climb_meters: float
    total_descent_meters: float
    turn_count: int
    longest_leg_distance_meters: float
    shortest_leg_distance_meters: float


class AnalyticsWarning(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str
    message: str


class MissionAnalyticsResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    summary: AnalyticsSummary
    statistics: AnalyticsStatistics
    warnings: list[AnalyticsWarning]
