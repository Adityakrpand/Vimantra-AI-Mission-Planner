from __future__ import annotations

from app.models.drone import DroneConnectionStatus, DroneTelemetrySnapshot
from app.models.mission import MissionRecord
from logging.audit import audit_event
from logging.constants import AuditEvent
from logging.context import log_context
from logging.logger import get_logger
from mission.validation_models import MissionValidationResult
from preflight.checks import mandatory_checks, optional_checks
from preflight.models import PreFlightCheck, PreFlightConfig, PreFlightResult
from preflight.status import PreFlightCheckStatus

logger = get_logger(__name__)


class PreFlightService:
    def __init__(self, config: PreFlightConfig) -> None:
        self._config = config

    def run(
        self,
        *,
        mission: MissionRecord,
        mission_validation: MissionValidationResult,
        drone_status: DroneConnectionStatus,
        telemetry: DroneTelemetrySnapshot,
        mission_loaded: bool,
        configuration_loaded: bool = True,
    ) -> PreFlightResult:
        with log_context(mission_id=mission.id):
            checks = [
                *mandatory_checks(
                    drone_status=drone_status,
                    mission_validation=mission_validation,
                    telemetry=telemetry,
                    mission_loaded=mission_loaded,
                    configuration_loaded=configuration_loaded,
                ),
                *optional_checks(
                    config=self._config,
                    mission_validation=mission_validation,
                    telemetry=telemetry,
                ),
            ]
            ready = all(
                check.status == PreFlightCheckStatus.PASS
                for check in checks
                if check.mandatory
            )
            warnings = [
                check for check in checks if check.status == PreFlightCheckStatus.WARNING
            ]
            score = _score(checks)
            result = PreFlightResult(
                ready=ready,
                score=score,
                checks=checks,
                warnings=warnings,
            )
            _log_result(result)
            audit_event(
                AuditEvent.PREFLIGHT_EXECUTED,
                "Pre-flight checks executed.",
                mission_id=mission.id,
                details={
                    "ready": result.ready,
                    "score": result.score,
                    "warnings": len(result.warnings),
                },
            )
            return result


def _score(checks: list[PreFlightCheck]) -> int:
    if not checks:
        return 0

    passed = sum(1 for check in checks if check.status == PreFlightCheckStatus.PASS)
    warning = sum(1 for check in checks if check.status == PreFlightCheckStatus.WARNING)
    weighted = passed + (warning * 0.5)
    return round((weighted / len(checks)) * 100)


def _log_result(result: PreFlightResult) -> None:
    if result.ready and not result.warnings:
        logger.info("Pre-flight result PASS score=%s", result.score)
    elif result.ready:
        logger.warning(
            "Pre-flight result WARNING score=%s warnings=%s",
            result.score,
            len(result.warnings),
        )
    else:
        logger.error("Pre-flight result FAIL score=%s", result.score)
