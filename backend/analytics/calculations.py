from __future__ import annotations

from math import atan2, cos, degrees, radians, sin, sqrt

from app.models.mission import MissionRecord, Waypoint
from analytics.constants import (
    BATTERY_BASE_USAGE_PERCENT,
    BATTERY_USAGE_PER_CLIMB_METER_PERCENT,
    BATTERY_USAGE_PER_KILOMETER_PERCENT,
    BATTERY_USAGE_PER_WAYPOINT_PERCENT,
    EARTH_RADIUS_METERS,
    SHARP_TURN_DEGREES,
)


def leg_distances_meters(mission: MissionRecord) -> list[float]:
    return [
        calculate_distance_meters(start, end)
        for start, end in zip(mission.waypoints, mission.waypoints[1:])
    ]


def calculate_distance_meters(start: Waypoint, end: Waypoint) -> float:
    start_latitude = radians(start.latitude)
    end_latitude = radians(end.latitude)
    latitude_delta = radians(end.latitude - start.latitude)
    longitude_delta = radians(end.longitude - start.longitude)
    haversine = (
        sin(latitude_delta / 2) * sin(latitude_delta / 2)
        + cos(start_latitude)
        * cos(end_latitude)
        * sin(longitude_delta / 2)
        * sin(longitude_delta / 2)
    )

    return EARTH_RADIUS_METERS * 2 * atan2(sqrt(haversine), sqrt(1 - haversine))


def total_distance_meters(mission: MissionRecord) -> float:
    return sum(leg_distances_meters(mission))


def estimated_flight_time_seconds(
    mission: MissionRecord,
    distances_meters: list[float],
) -> float:
    if not distances_meters:
        return 0.0

    total_seconds = 0.0
    for index, distance_meters in enumerate(distances_meters):
        speed = max(mission.waypoints[index].speed_meters_per_second, 0.01)
        total_seconds += distance_meters / speed

    return total_seconds


def altitude_extremes(mission: MissionRecord) -> tuple[float, float, float]:
    altitudes = [waypoint.altitude_meters for waypoint in mission.waypoints]
    if not altitudes:
        return 0.0, 0.0, 0.0

    return max(altitudes), min(altitudes), sum(altitudes) / len(altitudes)


def speed_statistics(mission: MissionRecord) -> tuple[float, float]:
    speeds = [waypoint.speed_meters_per_second for waypoint in mission.waypoints]
    if not speeds:
        return 0.0, 0.0

    return sum(speeds) / len(speeds), max(speeds)


def climb_and_descent_meters(mission: MissionRecord) -> tuple[float, float]:
    total_climb = 0.0
    total_descent = 0.0
    for start, end in zip(mission.waypoints, mission.waypoints[1:]):
        altitude_delta = end.altitude_meters - start.altitude_meters
        if altitude_delta > 0:
            total_climb += altitude_delta
        else:
            total_descent += abs(altitude_delta)

    return total_climb, total_descent


def turn_count(mission: MissionRecord) -> int:
    turns = 0
    for previous, current, next_waypoint in zip(
        mission.waypoints,
        mission.waypoints[1:],
        mission.waypoints[2:],
    ):
        if _turn_angle_degrees(previous, current, next_waypoint) >= SHARP_TURN_DEGREES:
            turns += 1

    return turns


def estimated_battery_usage_percent(
    *,
    distance_meters: float,
    total_climb_meters: float,
    waypoint_count: int,
) -> float:
    usage = (
        BATTERY_BASE_USAGE_PERCENT
        + ((distance_meters / 1000) * BATTERY_USAGE_PER_KILOMETER_PERCENT)
        + (total_climb_meters * BATTERY_USAGE_PER_CLIMB_METER_PERCENT)
        + (waypoint_count * BATTERY_USAGE_PER_WAYPOINT_PERCENT)
    )
    return min(100.0, usage)


def _turn_angle_degrees(
    previous: Waypoint,
    current: Waypoint,
    next_waypoint: Waypoint,
) -> float:
    vector_a = (
        current.latitude - previous.latitude,
        current.longitude - previous.longitude,
    )
    vector_b = (
        next_waypoint.latitude - current.latitude,
        next_waypoint.longitude - current.longitude,
    )
    magnitude_a = sqrt((vector_a[0] * vector_a[0]) + (vector_a[1] * vector_a[1]))
    magnitude_b = sqrt((vector_b[0] * vector_b[0]) + (vector_b[1] * vector_b[1]))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    dot_product = (vector_a[0] * vector_b[0]) + (vector_a[1] * vector_b[1])
    cosine = max(-1.0, min(1.0, dot_product / (magnitude_a * magnitude_b)))
    return degrees(atan2(sqrt(1 - (cosine * cosine)), cosine))
