from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt

from mission.validation_models import (
    MissionValidationIssue,
    MissionValidationRequest,
    MissionValidationWaypoint,
)


@dataclass(frozen=True)
class MissionValidationConfig:
    minimum_waypoints: int = 2
    minimum_altitude_meters: float = 5
    maximum_altitude_meters: float = 120
    minimum_speed_meters_per_second: float = 1
    maximum_speed_meters_per_second: float = 15
    high_speed_warning_meters_per_second: float = 12
    maximum_distance_warning_meters: float = 5000
    close_waypoint_warning_meters: float = 2


def validate_mission_name(mission: MissionValidationRequest) -> list[MissionValidationIssue]:
    if mission.name is None or mission.name.strip() == "":
        return [
            MissionValidationIssue(
                code="MISSION_NAME_REQUIRED",
                message="Mission name is required.",
            )
        ]

    return []


def validate_waypoint_count(
    mission: MissionValidationRequest,
    config: MissionValidationConfig,
) -> list[MissionValidationIssue]:
    if len(mission.waypoints) < config.minimum_waypoints:
        return [
            MissionValidationIssue(
                code="TOO_FEW_WAYPOINTS",
                message=f"Mission must contain at least {config.minimum_waypoints} waypoints.",
            )
        ]

    return []


def validate_waypoint_values(
    mission: MissionValidationRequest,
    config: MissionValidationConfig,
) -> list[MissionValidationIssue]:
    errors: list[MissionValidationIssue] = []

    for index, waypoint in enumerate(mission.waypoints, start=1):
        errors.extend(_validate_required_values(waypoint, index))
        if waypoint.latitude is not None and not -90 <= waypoint.latitude <= 90:
            errors.append(
                MissionValidationIssue(
                    code="LATITUDE_OUT_OF_RANGE",
                    waypoint=index,
                    message="Latitude must be between -90 and 90 degrees.",
                )
            )
        if waypoint.longitude is not None and not -180 <= waypoint.longitude <= 180:
            errors.append(
                MissionValidationIssue(
                    code="LONGITUDE_OUT_OF_RANGE",
                    waypoint=index,
                    message="Longitude must be between -180 and 180 degrees.",
                )
            )
        if (
            waypoint.altitude_meters is not None
            and waypoint.altitude_meters < config.minimum_altitude_meters
        ):
            errors.append(
                MissionValidationIssue(
                    code="ALTITUDE_TOO_LOW",
                    waypoint=index,
                    message=(
                        "Altitude must be at least "
                        f"{config.minimum_altitude_meters:g} meters."
                    ),
                )
            )
        if (
            waypoint.altitude_meters is not None
            and waypoint.altitude_meters > config.maximum_altitude_meters
        ):
            errors.append(
                MissionValidationIssue(
                    code="ALTITUDE_TOO_HIGH",
                    waypoint=index,
                    message=(
                        "Altitude must be no more than "
                        f"{config.maximum_altitude_meters:g} meters."
                    ),
                )
            )
        if (
            waypoint.speed_meters_per_second is not None
            and waypoint.speed_meters_per_second < config.minimum_speed_meters_per_second
        ):
            errors.append(
                MissionValidationIssue(
                    code="SPEED_TOO_LOW",
                    waypoint=index,
                    message=(
                        "Speed must be at least "
                        f"{config.minimum_speed_meters_per_second:g} m/s."
                    ),
                )
            )
        if (
            waypoint.speed_meters_per_second is not None
            and waypoint.speed_meters_per_second > config.maximum_speed_meters_per_second
        ):
            errors.append(
                MissionValidationIssue(
                    code="SPEED_TOO_HIGH",
                    waypoint=index,
                    message=(
                        "Speed must be no more than "
                        f"{config.maximum_speed_meters_per_second:g} m/s."
                    ),
                )
            )

    return errors


def validate_consecutive_duplicates(
    mission: MissionValidationRequest,
) -> list[MissionValidationIssue]:
    errors: list[MissionValidationIssue] = []

    for index, waypoint in enumerate(mission.waypoints[1:], start=2):
        previous = mission.waypoints[index - 2]
        if _has_complete_position(waypoint) and _has_complete_position(previous):
            if (
                waypoint.latitude == previous.latitude
                and waypoint.longitude == previous.longitude
                and waypoint.altitude_meters == previous.altitude_meters
            ):
                errors.append(
                    MissionValidationIssue(
                        code="DUPLICATE_CONSECUTIVE_WAYPOINT",
                        waypoint=index,
                        message="Consecutive waypoints cannot have the same position and altitude.",
                    )
                )

    return errors


def validate_nonzero_distance(
    mission: MissionValidationRequest,
    distance_meters: float,
) -> list[MissionValidationIssue]:
    if len(mission.waypoints) >= 2 and distance_meters == 0:
        return [
            MissionValidationIssue(
                code="ZERO_DISTANCE_MISSION",
                message="Mission distance cannot be zero.",
            )
        ]

    return []


def build_warnings(
    mission: MissionValidationRequest,
    config: MissionValidationConfig,
    distance_meters: float,
) -> list[MissionValidationIssue]:
    warnings: list[MissionValidationIssue] = []

    for index, waypoint in enumerate(mission.waypoints, start=1):
        if (
            waypoint.speed_meters_per_second is not None
            and waypoint.speed_meters_per_second >= config.high_speed_warning_meters_per_second
            and waypoint.speed_meters_per_second <= config.maximum_speed_meters_per_second
        ):
            warnings.append(
                MissionValidationIssue(
                    code="HIGH_SPEED",
                    waypoint=index,
                    message="Waypoint speed is high for a simulation mission.",
                )
            )

    if distance_meters > config.maximum_distance_warning_meters:
        warnings.append(
            MissionValidationIssue(
                code="MISSION_DISTANCE_HIGH",
                message="Mission distance is larger than 5 km.",
            )
        )

    for index, waypoint in enumerate(mission.waypoints[1:], start=2):
        previous = mission.waypoints[index - 2]
        if _has_complete_position(waypoint) and _has_complete_position(previous):
            segment_distance = calculate_distance_meters(previous, waypoint)
            if 0 < segment_distance < config.close_waypoint_warning_meters:
                warnings.append(
                    MissionValidationIssue(
                        code="WAYPOINTS_CLOSE_TOGETHER",
                        waypoint=index,
                        message="Waypoint is very close to the previous waypoint.",
                    )
                )

    return warnings


def calculate_total_distance_meters(mission: MissionValidationRequest) -> float:
    distance_meters = 0.0

    for index, waypoint in enumerate(mission.waypoints[1:], start=1):
        previous = mission.waypoints[index - 1]
        if _has_complete_position(previous) and _has_complete_position(waypoint):
            distance_meters += calculate_distance_meters(previous, waypoint)

    return distance_meters


def calculate_distance_meters(
    start: MissionValidationWaypoint,
    end: MissionValidationWaypoint,
) -> float:
    earth_radius_meters = 6371000
    start_latitude = radians(start.latitude or 0)
    end_latitude = radians(end.latitude or 0)
    latitude_delta = radians((end.latitude or 0) - (start.latitude or 0))
    longitude_delta = radians((end.longitude or 0) - (start.longitude or 0))
    haversine = (
        sin(latitude_delta / 2) * sin(latitude_delta / 2)
        + cos(start_latitude)
        * cos(end_latitude)
        * sin(longitude_delta / 2)
        * sin(longitude_delta / 2)
    )

    return earth_radius_meters * 2 * atan2(sqrt(haversine), sqrt(1 - haversine))


def _validate_required_values(
    waypoint: MissionValidationWaypoint,
    waypoint_index: int,
) -> list[MissionValidationIssue]:
    errors: list[MissionValidationIssue] = []
    required_fields = {
        "latitude": "Latitude",
        "longitude": "Longitude",
        "altitude_meters": "Altitude",
        "speed_meters_per_second": "Speed",
    }

    for field_name, label in required_fields.items():
        if getattr(waypoint, field_name) is None:
            errors.append(
                MissionValidationIssue(
                    code=f"{field_name.upper()}_REQUIRED",
                    waypoint=waypoint_index,
                    message=f"{label} is required.",
                )
            )

    return errors


def _has_complete_position(waypoint: MissionValidationWaypoint) -> bool:
    return (
        waypoint.latitude is not None
        and waypoint.longitude is not None
        and waypoint.altitude_meters is not None
    )

