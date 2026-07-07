from __future__ import annotations

import asyncio
from typing import Protocol

from mavsdk.mission import MissionItem, MissionPlan

from app.models.mission import MissionRecord, MissionUploadStatus, Waypoint
from app.services.drone_connection import DroneConnectionService
from app.services.mission_storage import MissionStorage
from logging.audit import audit_event
from logging.constants import AuditEvent
from logging.context import log_context
from logging.logger import get_logger
from mission.exceptions import MissionValidationError
from mission.validator import MissionValidator

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
        upload_timeout_seconds: float = 30,
    ) -> None:
        self._mission_storage = mission_storage
        self._drone_connection = drone_connection
        self._mission_validator = mission_validator or MissionValidator()
        self._upload_timeout_seconds = upload_timeout_seconds

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
