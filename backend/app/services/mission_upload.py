from __future__ import annotations

import asyncio
from typing import Protocol

from mavsdk.mission import MissionItem, MissionPlan

from app.models.mission import MissionRecord, MissionUploadStatus, Waypoint
from app.services.drone_connection import DroneConnectionService
from app.services.mission_storage import MissionStorage
from app.services.telemetry import TelemetryService
from config import defaults
from logging.audit import audit_event
from logging.constants import AuditEvent
from logging.context import log_context
from logging.logger import get_logger
from mission.exceptions import MissionValidationError
from mission.validator import MissionValidator
from preflight.exceptions import PreFlightCheckFailedError
from preflight.models import PreFlightConfig
from preflight.service import PreFlightService

logger = get_logger(__name__)


class MissionPlugin(Protocol):
    async def upload_mission(self, mission_plan: MissionPlan) -> None:
        ...


class MissionUploadService:
    def __init__(
        self,
        mission_storage: MissionStorage,
        drone_connection: DroneConnectionService,
        mission_validator: MissionValidator | None = None,
        preflight_service: PreFlightService | None = None,
        upload_timeout_seconds: float = 30,
        telemetry_timeout_seconds: float = 1,
    ) -> None:
        self._mission_storage = mission_storage
        self._drone_connection = drone_connection
        self._mission_validator = mission_validator or MissionValidator()
        self._preflight_service = preflight_service or PreFlightService(
            PreFlightConfig(
                battery_warning_threshold_percent=(
                    defaults.DEFAULT_PREFLIGHT_BATTERY_WARNING_THRESHOLD_PERCENT
                ),
                gps_minimum_satellites=defaults.DEFAULT_PREFLIGHT_GPS_MINIMUM_SATELLITES,
                optional_checks_enabled=defaults.DEFAULT_PREFLIGHT_OPTIONAL_CHECKS_ENABLED,
            )
        )
        self._upload_timeout_seconds = upload_timeout_seconds
        self._telemetry_timeout_seconds = telemetry_timeout_seconds

    async def upload_mission(self, mission_id: int) -> MissionUploadStatus:
        with log_context(mission_id=mission_id):
            mission = self._mission_storage.get_mission(mission_id)
            validation_result = self._mission_validator.validate(mission)
            if not validation_result.valid:
                logger.warning("Mission upload rejected by validation.")
                audit_event(
                    AuditEvent.MISSION_UPLOAD_FAILED,
                    "Mission upload failed validation.",
                    mission_id=mission_id,
                )
                raise MissionValidationError(validation_result)

            telemetry = await TelemetryService(
                self._drone_connection,
                timeout_seconds=self._telemetry_timeout_seconds,
            ).get_snapshot()
            preflight_result = self._preflight_service.run(
                mission=mission,
                mission_validation=validation_result,
                drone_status=self._drone_connection.status(),
                telemetry=telemetry,
                mission_loaded=True,
            )
            if not preflight_result.ready:
                audit_event(
                    AuditEvent.MISSION_UPLOAD_FAILED,
                    "Mission upload blocked by pre-flight checks.",
                    mission_id=mission_id,
                    level="ERROR",
                )
                raise PreFlightCheckFailedError(preflight_result)

            system = self._drone_connection.get_connected_system()
            mission_plan = MissionPlan(
                [_to_mavsdk_mission_item(waypoint) for waypoint in mission.waypoints]
            )

            mission_plugin = system.mission
            try:
                async with asyncio.timeout(self._upload_timeout_seconds):
                    await mission_plugin.upload_mission(mission_plan)
            except Exception:
                audit_event(
                    AuditEvent.MISSION_UPLOAD_FAILED,
                    "Mission upload failed.",
                    mission_id=mission_id,
                    level="ERROR",
                )
                raise

            self._drone_connection.mark_mission_loaded(mission_id)
            audit_event(
                AuditEvent.MISSION_UPLOADED,
                "Mission uploaded.",
                mission_id=mission_id,
                details={"waypoints": len(mission.waypoints)},
            )
            logger.info("Mission uploaded waypoint_count=%s", len(mission.waypoints))
            return MissionUploadStatus(
                mission_id=mission.id,
                uploaded=True,
                waypoint_count=len(mission.waypoints),
                message=f"Uploaded mission {mission.name}.",
            )


def _to_mavsdk_mission_item(waypoint: Waypoint) -> MissionItem:
    return MissionItem(
        waypoint.latitude,
        waypoint.longitude,
        waypoint.altitude_meters,
        waypoint.speed_meters_per_second,
        True,
        float("nan"),
        float("nan"),
        MissionItem.CameraAction.NONE,
        float("nan"),
        0,
        float("nan"),
        float("nan"),
        0,
        MissionItem.VehicleAction.NONE,
    )
