from __future__ import annotations

import math
from dataclasses import dataclass, field

from app.models.mission import MissionRecord, Waypoint
from validation.config import ValidationEngineConfig
from validation.models import CheckStatus, ValidationCheck, ValidationIssue

EARTH_RADIUS_METERS = 6_371_000
FULL_BATTERY_PERCENT = 100.0
BATTERY_DISTANCE_DIVISOR_METERS = 400.0
BATTERY_CLIMB_DIVISOR_METERS = 20.0
BATTERY_WAYPOINT_COST_PERCENT = 0.5
STRAIGHT_ANGLE_DEGREES = 180.0


@dataclass
class RuleContext:
    mission: MissionRecord
    config: ValidationEngineConfig
    distances_meters: list[float] = field(init=False)
    total_distance_meters: float = field(init=False)
    estimated_time_seconds: float = field(init=False)
    total_climb_meters: float = field(init=False)
    total_descent_meters: float = field(init=False)
    estimated_battery_usage_percent: float = field(init=False)
    estimated_battery_remaining_percent: float = field(init=False)
    turn_angles_degrees: list[float] = field(init=False)

    def __post_init__(self) -> None:
        self.distances_meters = leg_distances_meters(self.mission.waypoints)
        self.total_distance_meters = sum(self.distances_meters)
        self.estimated_time_seconds = estimated_flight_time_seconds(
            self.mission.waypoints,
            self.distances_meters,
        )
        self.total_climb_meters, self.total_descent_meters = altitude_totals(
            self.mission.waypoints
        )
        self.estimated_battery_usage_percent = estimated_battery_usage_percent(
            self.total_distance_meters,
            self.total_climb_meters,
            len(self.mission.waypoints),
        )
        self.estimated_battery_remaining_percent = max(
            0.0,
            FULL_BATTERY_PERCENT - self.estimated_battery_usage_percent,
        )
        self.turn_angles_degrees = turn_angles_degrees(self.mission.waypoints)


@dataclass
class RuleResult:
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    checks: list[ValidationCheck] = field(default_factory=list)

    def fail(
        self,
        *,
        code: str,
        message: str,
        category: str,
        name: str,
        waypoint: int | None = None,
    ) -> None:
        self.errors.append(
            ValidationIssue(
                code=code,
                message=message,
                category=category,
                waypoint=waypoint,
            )
        )
        self.checks.append(
            ValidationCheck(
                name=name,
                category=category,
                status=CheckStatus.FAIL,
                message=message,
            )
        )

    def warn(
        self,
        *,
        code: str,
        message: str,
        category: str,
        name: str,
        waypoint: int | None = None,
    ) -> None:
        self.warnings.append(
            ValidationIssue(
                code=code,
                message=message,
                category=category,
                waypoint=waypoint,
            )
        )
        self.checks.append(
            ValidationCheck(
                name=name,
                category=category,
                status=CheckStatus.WARNING,
                message=message,
            )
        )

    def pass_check(self, *, name: str, category: str, message: str) -> None:
        self.checks.append(
            ValidationCheck(
                name=name,
                category=category,
                status=CheckStatus.PASS,
                message=message,
            )
        )


def validate_waypoints(context: RuleContext) -> RuleResult:
    result = RuleResult()
    waypoints = context.mission.waypoints
    config = context.config

    if len(waypoints) == 0:
        result.fail(
            code="EMPTY_MISSION",
            message="Mission must contain at least one waypoint.",
            category="Waypoints",
            name="Empty Mission",
        )
    elif len(waypoints) < config.minimum_waypoints:
        result.fail(
            code="MINIMUM_WAYPOINTS",
            message=f"Mission must contain at least {config.minimum_waypoints} waypoints.",
            category="Waypoints",
            name="Minimum Waypoints",
        )
    else:
        result.pass_check(
            name="Minimum Waypoints",
            category="Waypoints",
            message="Mission has enough waypoints.",
        )

    if len(waypoints) > config.maximum_waypoints:
        result.fail(
            code="MAXIMUM_WAYPOINTS",
            message=f"Mission exceeds {config.maximum_waypoints} waypoints.",
            category="Waypoints",
            name="Maximum Waypoints",
        )
    else:
        result.pass_check(
            name="Maximum Waypoints",
            category="Waypoints",
            message="Mission waypoint count is within limit.",
        )

    duplicate_found = False
    invalid_coordinate_found = False
    for index, waypoint in enumerate(waypoints):
        if not -90 <= waypoint.latitude <= 90:
            invalid_coordinate_found = True
            result.fail(
                code="INVALID_LATITUDE",
                message="Waypoint latitude must be between -90 and 90 degrees.",
                category="Waypoints",
                name="Latitude Range",
                waypoint=waypoint.sequence,
            )
        if not -180 <= waypoint.longitude <= 180:
            invalid_coordinate_found = True
            result.fail(
                code="INVALID_LONGITUDE",
                message="Waypoint longitude must be between -180 and 180 degrees.",
                category="Waypoints",
                name="Longitude Range",
                waypoint=waypoint.sequence,
            )
        if index > 0 and same_position(waypoints[index - 1], waypoint):
            duplicate_found = True
            result.fail(
                code="DUPLICATE_WAYPOINT",
                message="Consecutive waypoints cannot use identical coordinates.",
                category="Waypoints",
                name="Duplicate Consecutive Waypoints",
                waypoint=waypoint.sequence,
            )

    if not invalid_coordinate_found:
        result.pass_check(
            name="Coordinate Ranges",
            category="Waypoints",
            message="Waypoint coordinates are valid.",
        )
    if not duplicate_found:
        result.pass_check(
            name="Duplicate Consecutive Waypoints",
            category="Waypoints",
            message="No duplicate consecutive waypoints found.",
        )

    return result


def validate_distance(context: RuleContext) -> RuleResult:
    result = RuleResult()
    config = context.config

    if context.total_distance_meters > config.maximum_mission_distance_meters:
        result.fail(
            code="MAXIMUM_MISSION_DISTANCE",
            message="Mission distance exceeds the configured maximum.",
            category="Distance",
            name="Maximum Mission Distance",
        )
    else:
        result.pass_check(
            name="Maximum Mission Distance",
            category="Distance",
            message="Mission distance is within the configured maximum.",
        )

    long_leg_found = False
    close_leg_found = False
    for index, distance in enumerate(context.distances_meters, start=2):
        if distance > config.maximum_single_leg_distance_meters:
            long_leg_found = True
            result.fail(
                code="MAXIMUM_SINGLE_LEG_DISTANCE",
                message="Single-leg distance exceeds the configured maximum.",
                category="Distance",
                name="Maximum Single-Leg Distance",
                waypoint=index,
            )
        if distance < config.minimum_waypoint_spacing_meters:
            close_leg_found = True
            result.fail(
                code="MINIMUM_WAYPOINT_DISTANCE",
                message="Waypoint spacing is below the configured minimum.",
                category="Distance",
                name="Minimum Waypoint Spacing",
                waypoint=index,
            )

    if not long_leg_found:
        result.pass_check(
            name="Maximum Single-Leg Distance",
            category="Distance",
            message="Every leg distance is within limit.",
        )
    if not close_leg_found:
        result.pass_check(
            name="Minimum Waypoint Spacing",
            category="Distance",
            message="Waypoint spacing is acceptable.",
        )

    return result


def validate_altitude(context: RuleContext) -> RuleResult:
    result = RuleResult()
    config = context.config
    low_or_high_found = False
    jump_found = False
    climb_found = False
    descent_found = False

    for index, waypoint in enumerate(context.mission.waypoints):
        if waypoint.altitude_meters < config.minimum_altitude_meters:
            low_or_high_found = True
            result.fail(
                code="ALTITUDE_TOO_LOW",
                message="Waypoint altitude is below the configured minimum.",
                category="Altitude",
                name="Altitude Limit",
                waypoint=waypoint.sequence,
            )
        if waypoint.altitude_meters > config.maximum_altitude_meters:
            low_or_high_found = True
            result.fail(
                code="ALTITUDE_TOO_HIGH",
                message="Waypoint altitude exceeds the configured maximum.",
                category="Altitude",
                name="Altitude Limit",
                waypoint=waypoint.sequence,
            )
        if index == 0:
            continue
        previous = context.mission.waypoints[index - 1]
        altitude_delta = waypoint.altitude_meters - previous.altitude_meters
        distance = context.distances_meters[index - 1]
        speed = max(waypoint.speed_meters_per_second, 0.001)
        leg_time = distance / speed if distance > 0 else 0
        rate = abs(altitude_delta) / leg_time if leg_time > 0 else abs(altitude_delta)

        if abs(altitude_delta) > config.maximum_altitude_jump_meters:
            jump_found = True
            result.warn(
                code="SUDDEN_ALTITUDE_JUMP",
                message="Altitude change between waypoints is abrupt.",
                category="Altitude",
                name="Sudden Altitude Jump",
                waypoint=waypoint.sequence,
            )
        if altitude_delta > 0 and rate > config.maximum_climb_rate_meters_per_second:
            climb_found = True
            result.fail(
                code="CLIMB_RATE_TOO_HIGH",
                message="Required climb rate exceeds the configured safety limit.",
                category="Altitude",
                name="Safe Climb Rate",
                waypoint=waypoint.sequence,
            )
        if altitude_delta < 0 and rate > config.maximum_descent_rate_meters_per_second:
            descent_found = True
            result.fail(
                code="DESCENT_RATE_TOO_HIGH",
                message="Required descent rate exceeds the configured safety limit.",
                category="Altitude",
                name="Safe Descent Rate",
                waypoint=waypoint.sequence,
            )

    if not low_or_high_found:
        result.pass_check(
            name="Altitude Limit",
            category="Altitude",
            message="Waypoint altitudes are within limits.",
        )
    if not jump_found:
        result.pass_check(
            name="Sudden Altitude Jump",
            category="Altitude",
            message="Altitude changes are gradual.",
        )
    if not climb_found:
        result.pass_check(
            name="Safe Climb Rate",
            category="Altitude",
            message="Climb rate is within safety limit.",
        )
    if not descent_found:
        result.pass_check(
            name="Safe Descent Rate",
            category="Altitude",
            message="Descent rate is within safety limit.",
        )

    return result


def validate_speed(context: RuleContext) -> RuleResult:
    result = RuleResult()
    config = context.config
    invalid_speed_found = False
    cruise_warning_found = False

    for waypoint in context.mission.waypoints:
        if waypoint.speed_meters_per_second < config.minimum_speed_meters_per_second:
            invalid_speed_found = True
            result.fail(
                code="SPEED_TOO_LOW",
                message="Waypoint speed is below the configured minimum.",
                category="Speed",
                name="Minimum Speed",
                waypoint=waypoint.sequence,
            )
        if waypoint.speed_meters_per_second > config.maximum_speed_meters_per_second:
            invalid_speed_found = True
            result.fail(
                code="SPEED_TOO_HIGH",
                message="Waypoint speed exceeds the configured maximum.",
                category="Speed",
                name="Maximum Speed",
                waypoint=waypoint.sequence,
            )
        if waypoint.speed_meters_per_second > config.cruise_speed_meters_per_second:
            cruise_warning_found = True
            result.warn(
                code="CRUISE_SPEED_HIGH",
                message="Waypoint speed is above the recommended cruise speed.",
                category="Speed",
                name="Cruise Speed",
                waypoint=waypoint.sequence,
            )

    if not invalid_speed_found:
        result.pass_check(
            name="Speed Limits",
            category="Speed",
            message="Waypoint speeds are within mandatory limits.",
        )
    if not cruise_warning_found:
        result.pass_check(
            name="Cruise Speed",
            category="Speed",
            message="Waypoint speeds are within cruise recommendation.",
        )

    return result


def validate_flight_time(context: RuleContext) -> RuleResult:
    result = RuleResult()
    if context.estimated_time_seconds > context.config.maximum_flight_time_seconds:
        result.fail(
            code="MAXIMUM_FLIGHT_TIME",
            message="Estimated flight time exceeds the configured maximum.",
            category="Flight Time",
            name="Maximum Flight Duration",
        )
    else:
        result.pass_check(
            name="Maximum Flight Duration",
            category="Flight Time",
            message="Estimated flight time is within limit.",
        )

    return result


def validate_battery(context: RuleContext) -> RuleResult:
    result = RuleResult()
    config = context.config

    if context.estimated_battery_usage_percent > config.maximum_battery_usage_percent:
        result.fail(
            code="BATTERY_USAGE_TOO_HIGH",
            message="Estimated battery usage exceeds the configured maximum.",
            category="Battery",
            name="Battery Usage",
        )
    else:
        result.pass_check(
            name="Battery Usage",
            category="Battery",
            message="Estimated battery usage is within limit.",
        )

    if context.estimated_battery_remaining_percent < config.minimum_battery_reserve_percent:
        result.fail(
            code="LOW_BATTERY_RESERVE",
            message="Estimated battery reserve is below the configured minimum.",
            category="Battery",
            name="Required Reserve Battery",
        )
    else:
        result.pass_check(
            name="Required Reserve Battery",
            category="Battery",
            message="Estimated battery reserve is sufficient.",
        )

    return result


def validate_geometry(context: RuleContext) -> RuleResult:
    result = RuleResult()

    if len(context.mission.waypoints) < 2:
        result.fail(
            code="INVALID_PATH",
            message="Mission path requires at least two waypoints.",
            category="Geometry",
            name="Valid Path",
        )
    else:
        result.pass_check(
            name="Valid Path",
            category="Geometry",
            message="Mission path contains enough points to form a route.",
        )

    sharp_error_found = False
    sharp_warning_found = False
    for index, angle in enumerate(context.turn_angles_degrees, start=2):
        turn_deflection = STRAIGHT_ANGLE_DEGREES - angle
        if turn_deflection >= context.config.sharp_turn_error_degrees:
            sharp_error_found = True
            result.fail(
                code="EXTREMELY_SHARP_TURN",
                message="Mission path contains an extremely sharp turn.",
                category="Geometry",
                name="Sharp Turn Limit",
                waypoint=index,
            )
        elif turn_deflection >= context.config.sharp_turn_warning_degrees:
            sharp_warning_found = True
            result.warn(
                code="SHARP_TURN",
                message="Mission path contains a sharp turn.",
                category="Geometry",
                name="Sharp Turn Warning",
                waypoint=index,
            )

    if not sharp_error_found:
        result.pass_check(
            name="Sharp Turn Limit",
            category="Geometry",
            message="No extremely sharp turns found.",
        )
    if not sharp_warning_found:
        result.pass_check(
            name="Sharp Turn Warning",
            category="Geometry",
            message="No sharp turn warnings found.",
        )

    return result


def leg_distances_meters(waypoints: list[Waypoint]) -> list[float]:
    return [
        haversine_distance_meters(start, end)
        for start, end in zip(waypoints, waypoints[1:])
    ]


def estimated_flight_time_seconds(
    waypoints: list[Waypoint],
    distances_meters: list[float],
) -> float:
    total = 0.0
    for index, distance in enumerate(distances_meters, start=1):
        speed = waypoints[index].speed_meters_per_second
        if speed <= 0:
            continue
        total += distance / speed

    return total


def altitude_totals(waypoints: list[Waypoint]) -> tuple[float, float]:
    climb = 0.0
    descent = 0.0
    for start, end in zip(waypoints, waypoints[1:]):
        delta = end.altitude_meters - start.altitude_meters
        if delta > 0:
            climb += delta
        else:
            descent += abs(delta)

    return climb, descent


def estimated_battery_usage_percent(
    distance_meters: float,
    total_climb_meters: float,
    waypoint_count: int,
) -> float:
    return min(
        FULL_BATTERY_PERCENT,
        distance_meters / BATTERY_DISTANCE_DIVISOR_METERS
        + total_climb_meters / BATTERY_CLIMB_DIVISOR_METERS
        + waypoint_count * BATTERY_WAYPOINT_COST_PERCENT,
    )


def turn_angles_degrees(waypoints: list[Waypoint]) -> list[float]:
    angles: list[float] = []
    if len(waypoints) < 3:
        return angles

    for previous, current, following in zip(waypoints, waypoints[1:], waypoints[2:]):
        vector_a = (
            previous.latitude - current.latitude,
            previous.longitude - current.longitude,
        )
        vector_b = (
            following.latitude - current.latitude,
            following.longitude - current.longitude,
        )
        magnitude_a = math.hypot(*vector_a)
        magnitude_b = math.hypot(*vector_b)
        if magnitude_a == 0 or magnitude_b == 0:
            continue
        dot_product = vector_a[0] * vector_b[0] + vector_a[1] * vector_b[1]
        cosine = max(-1.0, min(1.0, dot_product / (magnitude_a * magnitude_b)))
        angles.append(math.degrees(math.acos(cosine)))

    return angles


def haversine_distance_meters(start: Waypoint, end: Waypoint) -> float:
    start_latitude = math.radians(start.latitude)
    end_latitude = math.radians(end.latitude)
    latitude_delta = math.radians(end.latitude - start.latitude)
    longitude_delta = math.radians(end.longitude - start.longitude)
    haversine = (
        math.sin(latitude_delta / 2) ** 2
        + math.cos(start_latitude)
        * math.cos(end_latitude)
        * math.sin(longitude_delta / 2) ** 2
    )
    return EARTH_RADIUS_METERS * 2 * math.atan2(
        math.sqrt(haversine),
        math.sqrt(1 - haversine),
    )


def same_position(start: Waypoint, end: Waypoint) -> bool:
    return start.latitude == end.latitude and start.longitude == end.longitude
