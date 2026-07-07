from __future__ import annotations

from typing import Protocol

from app.models.drone import DroneActionStatus
from app.services.drone_connection import DroneConnectionService
from logging.audit import audit_event
from logging.constants import AuditEvent
from logging.logger import get_logger

logger = get_logger(__name__)


class ActionPlugin(Protocol):
    async def arm(self) -> None:
        ...

    async def disarm(self) -> None:
        ...


class MissionPlugin(Protocol):
    async def start_mission(self) -> None:
        ...


class DroneActionService:
    def __init__(self, drone_connection: DroneConnectionService) -> None:
        self._drone_connection = drone_connection

    async def arm(self) -> DroneActionStatus:
        system = self._drone_connection.get_connected_system()
        action_plugin: ActionPlugin = system.action
        await action_plugin.arm()
        audit_event(AuditEvent.VEHICLE_ARMED, "Vehicle armed.")
        logger.info("Vehicle armed.")

        return DroneActionStatus(
            completed=True,
            action="arm",
            message="Drone armed.",
        )

    async def disarm(self) -> DroneActionStatus:
        system = self._drone_connection.get_connected_system()
        action_plugin: ActionPlugin = system.action
        await action_plugin.disarm()
        audit_event(AuditEvent.VEHICLE_DISARMED, "Vehicle disarmed.")
        logger.info("Vehicle disarmed.")

        return DroneActionStatus(
            completed=True,
            action="disarm",
            message="Drone disarmed.",
        )

    async def start_mission(self) -> DroneActionStatus:
        system = self._drone_connection.get_connected_system()
        mission_plugin: MissionPlugin = system.mission
        await mission_plugin.start_mission()
        audit_event(AuditEvent.MISSION_STARTED, "Mission started.")
        logger.info("Mission started.")

        return DroneActionStatus(
            completed=True,
            action="start_mission",
            message="Mission started.",
        )
