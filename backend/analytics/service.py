from __future__ import annotations

from app.models.mission import MissionRecord
from analytics.calculations import (
    altitude_extremes,
    climb_and_descent_meters,
    estimated_battery_usage_percent,
    estimated_flight_time_seconds,
    leg_distances_meters,
    speed_statistics,
    total_distance_meters,
    turn_count,
)
from analytics.exceptions import MissionAnalyticsError
from analytics.models import (
    AnalyticsStatistics,
    AnalyticsSummary,
    AnalyticsWarning,
    MissionAnalyticsConfig,
    MissionAnalyticsResult,
)
from logging.logger import get_logger

logger = get_logger(__name__)


class MissionAnalyticsService:
    def __init__(self, config: MissionAnalyticsConfig) -> None:
        self._config = config

    def generate(self, mission: MissionRecord) -> MissionAnalyticsResult:
        try:
            distances = leg_distances_meters(mission)
            distance_meters = total_distance_meters(mission)
            flight_time_seconds = estimated_flight_time_seconds(mission, distances)
            maximum_altitude, minimum_altitude, average_altitude = altitude_extremes(
                mission
            )
            average_speed, maximum_speed = speed_statistics(mission)
            total_climb, total_descent = climb_and_descent_meters(mission)
            turns = turn_count(mission)
            battery_usage = estimated_battery_usage_percent(
                distance_meters=distance_meters,
                total_climb_meters=total_climb,
                waypoint_count=len(mission.waypoints),
            )
            battery_remaining = max(0.0, 100.0 - battery_usage)
            summary = AnalyticsSummary(
                distance_meters=round(distance_meters, 2),
                estimated_flight_time_seconds=round(flight_time_seconds, 2),
                estimated_battery_usage_percent=round(battery_usage, 2),
                estimated_battery_remaining_percent=round(battery_remaining, 2),
                waypoint_count=len(mission.waypoints),
            )
            statistics = AnalyticsStatistics(
                maximum_altitude_meters=round(maximum_altitude, 2),
                minimum_altitude_meters=round(minimum_altitude, 2),
                average_altitude_meters=round(average_altitude, 2),
                average_speed_meters_per_second=round(average_speed, 2),
                maximum_speed_meters_per_second=round(maximum_speed, 2),
                total_climb_meters=round(total_climb, 2),
                total_descent_meters=round(total_descent, 2),
                turn_count=turns,
                longest_leg_distance_meters=round(max(distances, default=0.0), 2),
                shortest_leg_distance_meters=round(min(distances, default=0.0), 2),
            )
            warnings = self._warnings(
                summary=summary,
                statistics=statistics,
            )
            if warnings:
                logger.warning("Mission analytics generated warnings=%s", len(warnings))
            logger.info(
                "Mission analytics generated mission_id=%s distance_meters=%s",
                mission.id,
                summary.distance_meters,
            )
            return MissionAnalyticsResult(
                summary=summary,
                statistics=statistics,
                warnings=warnings,
            )
        except Exception as error:
            logger.exception("Mission analytics calculation failed mission_id=%s", mission.id)
            raise MissionAnalyticsError("Mission analytics calculation failed.") from error

    def _warnings(
        self,
        *,
        summary: AnalyticsSummary,
        statistics: AnalyticsStatistics,
    ) -> list[AnalyticsWarning]:
        warnings: list[AnalyticsWarning] = []
        if summary.distance_meters > self._config.maximum_recommended_distance_meters:
            warnings.append(
                AnalyticsWarning(
                    code="MISSION_DISTANCE_HIGH",
                    message="Mission distance is above the recommended threshold.",
                )
            )
        if (
            summary.estimated_battery_remaining_percent
            < self._config.battery_warning_threshold_percent
        ):
            warnings.append(
                AnalyticsWarning(
                    code="BATTERY_REMAINING_LOW",
                    message="Estimated battery remaining is below the warning threshold.",
                )
            )
        if (
            statistics.average_speed_meters_per_second
            > self._config.average_speed_warning_meters_per_second
        ):
            warnings.append(
                AnalyticsWarning(
                    code="AVERAGE_SPEED_HIGH",
                    message="Average speed is above the recommended value.",
                )
            )
        if statistics.total_climb_meters > self._config.maximum_recommended_climb_meters:
            warnings.append(
                AnalyticsWarning(
                    code="CLIMB_HIGH",
                    message="Total climb is above the recommended threshold.",
                )
            )
        if statistics.turn_count > self._config.sharp_turn_warning_count:
            warnings.append(
                AnalyticsWarning(
                    code="SHARP_TURNS_HIGH",
                    message="Mission contains many sharp turns.",
                )
            )

        return warnings
