from __future__ import annotations

from typing import Protocol

from mavsdk.mission import MissionItem, MissionPlan

from app.models.mission import MissionRecord, MissionUploadStatus, Waypoint
from app.services.drone_connection import DroneConnectionService
from app.services.mission_storage import MissionStorage
from mission.exceptions import MissionValidationError
from mission.validator import MissionValidator


class MissionPlugin(Protocol):
    async def upload_mission(self, mission_plan: MissionPlan) -> None:
        ...


class MissionUploadService:
    def __init__(
        self,
        mission_storage: MissionStorage,
        drone_connection: DroneConnectionService,
        mission_validator: MissionValidator | None = None,
    ) -> None:
        self._mission_storage = mission_storage
        self._drone_connection = drone_connection
        self._mission_validator = mission_validator or MissionValidator()

    async def upload_mission(self, mission_id: int) -> MissionUploadStatus:
        mission = self._mission_storage.get_mission(mission_id)
        validation_result = self._mission_validator.validate(mission)
        if not validation_result.valid:
            raise MissionValidationError(validation_result)

        system = self._drone_connection.get_connected_system()
        mission_plan = MissionPlan(
            [_to_mavsdk_mission_item(waypoint) for waypoint in mission.waypoints]
        )

        mission_plugin = system.mission
        await mission_plugin.upload_mission(mission_plan)

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
