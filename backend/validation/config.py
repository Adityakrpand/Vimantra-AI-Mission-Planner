from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ValidationEngineConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    minimum_waypoints: int
    maximum_waypoints: int
    minimum_altitude_meters: float
    maximum_altitude_meters: float
    maximum_altitude_jump_meters: float
    maximum_climb_rate_meters_per_second: float
    maximum_descent_rate_meters_per_second: float
    minimum_speed_meters_per_second: float
    cruise_speed_meters_per_second: float
    maximum_speed_meters_per_second: float
    maximum_mission_distance_meters: float
    maximum_single_leg_distance_meters: float
    minimum_waypoint_spacing_meters: float
    maximum_flight_time_seconds: float
    maximum_battery_usage_percent: float
    minimum_battery_reserve_percent: float
    sharp_turn_warning_degrees: float
    sharp_turn_error_degrees: float
