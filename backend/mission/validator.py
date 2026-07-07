from __future__ import annotations

from app.models.mission import MissionRecord
from logging.audit import audit_event
from logging.constants import AuditEvent
from logging.logger import get_logger
from mission.validation_models import (
    MissionValidationRequest,
    MissionValidationResult,
    MissionValidationStatistics,
    MissionValidationWaypoint,
)
from mission.validation_rules import (
    MissionValidationConfig,
    build_warnings,
    calculate_total_distance_meters,
    validate_consecutive_duplicates,
    validate_mission_name,
    validate_nonzero_distance,
    validate_waypoint_count,
    validate_waypoint_values,
)

logger = get_logger(__name__)


class MissionValidator:
    def __init__(self, config: MissionValidationConfig | None = None) -> None:
        self._config = config or MissionValidationConfig()

    def validate(
        self,
        mission: MissionValidationRequest | MissionRecord,
    ) -> MissionValidationResult:
        validation_request = _to_validation_request(mission)
        distance_meters = calculate_total_distance_meters(validation_request)
        errors = [
            *validate_mission_name(validation_request),
            *validate_waypoint_count(validation_request, self._config),
            *validate_waypoint_values(validation_request, self._config),
            *validate_consecutive_duplicates(validation_request),
            *validate_nonzero_distance(validation_request, distance_meters),
        ]
        warnings = build_warnings(validation_request, self._config, distance_meters)
        result = MissionValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            statistics=MissionValidationStatistics(
                waypoints=len(validation_request.waypoints),
                distance=round(distance_meters, 2),
            ),
        )

        if result.valid:
            logger.info("Mission validated.")
        else:
            logger.error("Mission validation failed.")

        if result.warnings:
            logger.warning("Mission contains warnings.")

        audit_event(
            AuditEvent.MISSION_VALIDATED,
            "Mission validation completed.",
            details={
                "valid": result.valid,
                "errors": len(result.errors),
                "warnings": len(result.warnings),
            },
        )
        return result


def _to_validation_request(
    mission: MissionValidationRequest | MissionRecord,
) -> MissionValidationRequest:
    if isinstance(mission, MissionValidationRequest):
        return mission

    return MissionValidationRequest(
        name=mission.name,
        waypoints=[
            MissionValidationWaypoint(
                sequence=waypoint.sequence,
                latitude=waypoint.latitude,
                longitude=waypoint.longitude,
                altitude_meters=waypoint.altitude_meters,
                speed_meters_per_second=waypoint.speed_meters_per_second,
            )
            for waypoint in mission.waypoints
        ],
    )
