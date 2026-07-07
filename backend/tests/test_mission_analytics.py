from __future__ import annotations

from datetime import datetime, timezone

from analytics.calculations import (
    estimated_battery_usage_percent,
    estimated_flight_time_seconds,
    leg_distances_meters,
    turn_count,
)
from analytics.models import MissionAnalyticsConfig
from analytics.service import MissionAnalyticsService
from app.models.mission import MissionRecord, Waypoint


def test_distance_calculation() -> None:
    distances = leg_distances_meters(mission())

    assert round(sum(distances), 2) > 1000


def test_flight_time_calculation() -> None:
    sample = mission(speed=10)
    distances = leg_distances_meters(sample)

    assert estimated_flight_time_seconds(sample, distances) == sum(distances) / 10


def test_battery_estimation() -> None:
    usage = estimated_battery_usage_percent(
        distance_meters=2000,
        total_climb_meters=50,
        waypoint_count=4,
    )

    assert usage == 13


def test_turn_count() -> None:
    sample = mission(
        waypoints=[
            point(1, 19.0, 72.0),
            point(2, 19.0, 72.01),
            point(3, 18.99, 72.01),
        ]
    )

    assert turn_count(sample) == 0


def test_zero_distance_mission() -> None:
    sample = mission(waypoints=[point(1, 19.0, 72.0), point(2, 19.0, 72.0)])

    result = service().generate(sample)

    assert result.summary.distance_meters == 0
    assert result.summary.estimated_flight_time_seconds == 0


def test_single_waypoint_mission() -> None:
    result = service().generate(mission(waypoints=[point(1, 19.0, 72.0)]))

    assert result.summary.waypoint_count == 1
    assert result.statistics.longest_leg_distance_meters == 0
    assert result.statistics.shortest_leg_distance_meters == 0


def test_large_mission_generates_warnings() -> None:
    sample = mission(
        waypoints=[
            point(1, 19.0, 72.0, altitude=10, speed=20),
            point(2, 19.2, 72.2, altitude=180, speed=20),
            point(3, 19.0, 72.4, altitude=20, speed=20),
            point(4, 19.2, 72.6, altitude=190, speed=20),
        ]
    )

    result = service(
        MissionAnalyticsConfig(
            maximum_recommended_distance_meters=1000,
            battery_warning_threshold_percent=95,
            average_speed_warning_meters_per_second=12,
            maximum_recommended_climb_meters=50,
            sharp_turn_warning_count=0,
        )
    ).generate(sample)

    assert {warning.code for warning in result.warnings} >= {
        "MISSION_DISTANCE_HIGH",
        "BATTERY_REMAINING_LOW",
        "AVERAGE_SPEED_HIGH",
        "CLIMB_HIGH",
    }


def service(config: MissionAnalyticsConfig | None = None) -> MissionAnalyticsService:
    return MissionAnalyticsService(
        config
        or MissionAnalyticsConfig(
            maximum_recommended_distance_meters=5000,
            battery_warning_threshold_percent=25,
            average_speed_warning_meters_per_second=12,
            maximum_recommended_climb_meters=100,
            sharp_turn_warning_count=5,
        )
    )


def mission(
    *,
    speed: float = 8,
    waypoints: list[Waypoint] | None = None,
) -> MissionRecord:
    return MissionRecord(
        id=1,
        name="Analytics Mission",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        waypoints=waypoints
        or [
            point(1, 19.076, 72.8777, altitude=80, speed=speed),
            point(2, 19.0821, 72.8903, altitude=90, speed=speed),
            point(3, 19.0664, 72.9008, altitude=70, speed=speed),
        ],
    )


def point(
    sequence: int,
    latitude: float,
    longitude: float,
    *,
    altitude: float = 80,
    speed: float = 8,
) -> Waypoint:
    return Waypoint(
        sequence=sequence,
        latitude=latitude,
        longitude=longitude,
        altitude_meters=altitude,
        speed_meters_per_second=speed,
    )
