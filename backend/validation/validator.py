from __future__ import annotations

from app.models.mission import MissionRecord
from logging.logger import get_logger
from validation.config import ValidationEngineConfig
from validation.models import (
    CheckStatus,
    MissionValidationResponse,
    ValidationStatus,
    ValidationSummary,
)
from validation.rules import (
    RuleContext,
    RuleResult,
    validate_altitude,
    validate_battery,
    validate_distance,
    validate_flight_time,
    validate_geometry,
    validate_speed,
    validate_waypoints,
)

logger = get_logger(__name__)


class MissionValidationEngine:
    def __init__(self, config: ValidationEngineConfig) -> None:
        self._config = config

    def validate(self, mission: MissionRecord) -> MissionValidationResponse:
        context = RuleContext(mission=mission, config=self._config)
        results = [
            validate_waypoints(context),
            validate_distance(context),
            validate_altitude(context),
            validate_speed(context),
            validate_flight_time(context),
            validate_battery(context),
            validate_geometry(context),
        ]
        merged = self._merge(results)
        score = self._score(merged)
        status = self._status(merged, score)
        passed_checks = sum(
            1 for check in merged.checks if check.status == CheckStatus.PASS
        )
        failed_checks = sum(
            1 for check in merged.checks if check.status == CheckStatus.FAIL
        )
        response = MissionValidationResponse(
            status=status,
            score=score,
            errors=merged.errors,
            warnings=merged.warnings,
            checks=merged.checks,
            summary=ValidationSummary(
                errors=len(merged.errors),
                warnings=len(merged.warnings),
                passed=len(merged.errors) == 0,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
            ),
        )
        logger.info(
            "Mission validation generated.",
            extra={
                "mission_id": mission.id,
                "status": response.status,
                "score": response.score,
                "errors": response.summary.errors,
                "warnings": response.summary.warnings,
            },
        )
        return response

    @staticmethod
    def _merge(results: list[RuleResult]) -> RuleResult:
        merged = RuleResult()
        for result in results:
            merged.errors.extend(result.errors)
            merged.warnings.extend(result.warnings)
            merged.checks.extend(result.checks)

        return merged

    @staticmethod
    def _score(result: RuleResult) -> int:
        score = 100 - len(result.errors) * 15 - len(result.warnings) * 5
        return max(0, min(100, score))

    @staticmethod
    def _status(result: RuleResult, score: int) -> ValidationStatus:
        if result.errors:
            return ValidationStatus.UNSAFE if score < 70 else ValidationStatus.WARNING
        if result.warnings:
            return ValidationStatus.WARNING
        return ValidationStatus.READY
