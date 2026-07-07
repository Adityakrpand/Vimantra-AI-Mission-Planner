from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from typing import Protocol

from mavsdk import System

from app.models.drone import DroneConnectionStatus
from logging.audit import audit_event
from logging.constants import AuditEvent
from logging.logger import get_logger

logger = get_logger(__name__)


class ConnectionState(Protocol):
    is_connected: bool


class CoreTelemetry(Protocol):
    def connection_state(self) -> AsyncIterator[ConnectionState]:
        ...


class DroneSystem(Protocol):
    action: object
    core: CoreTelemetry
    mission: object
    telemetry: object

    async def connect(self, system_address: str | None = None) -> None:
        ...


class DroneConnectionTimeoutError(Exception):
    def __init__(self, system_address: str, timeout_seconds: float) -> None:
        super().__init__(
            f"Timed out connecting to {system_address} after {timeout_seconds:g} seconds."
        )
        self.system_address = system_address
        self.timeout_seconds = timeout_seconds


class DroneConnectionService:
    def __init__(
        self,
        system_factory: Callable[[], DroneSystem] | None = None,
    ) -> None:
        self._system_factory = system_factory or System
        self._system: DroneSystem | None = None
        self._system_address: str | None = None
        self._connected = False

    async def connect(
        self,
        system_address: str,
        timeout_seconds: float,
    ) -> DroneConnectionStatus:
        system = self._system_factory()
        try:
            async with asyncio.timeout(timeout_seconds):
                await system.connect(system_address=system_address)
                await self._wait_until_connected(system, system_address, timeout_seconds)
        except TimeoutError as error:
            logger.warning(
                "Drone connection timed out system_address=%s timeout_seconds=%s",
                system_address,
                timeout_seconds,
            )
            raise DroneConnectionTimeoutError(system_address, timeout_seconds) from error

        self._system = system
        self._system_address = system_address
        self._connected = True
        audit_event(
            AuditEvent.DRONE_CONNECTED,
            "Drone connected.",
            details={"system_address": system_address},
        )

        return self.status(message="Connected to drone.")

    async def disconnect(self) -> DroneConnectionStatus:
        self._system = None
        self._system_address = None
        self._connected = False
        audit_event(AuditEvent.DRONE_DISCONNECTED, "Drone disconnected.")

        return self.status(message="Drone connection cleared.")

    def status(self, message: str | None = None) -> DroneConnectionStatus:
        if self._connected:
            return DroneConnectionStatus(
                connected=True,
                system_address=self._system_address,
                message=message or "Drone connected.",
            )

        return DroneConnectionStatus(
            connected=False,
            system_address=None,
            message=message or "Drone disconnected.",
        )

    def get_connected_system(self) -> DroneSystem:
        if self._system is None or not self._connected:
            raise DroneNotConnectedError()

        return self._system

    async def _wait_until_connected(
        self,
        system: DroneSystem,
        system_address: str,
        timeout_seconds: float,
    ) -> None:
        try:
            async with asyncio.timeout(timeout_seconds):
                async for state in system.core.connection_state():
                    if state.is_connected:
                        return
        except TimeoutError as error:
            raise DroneConnectionTimeoutError(system_address, timeout_seconds) from error

        raise DroneConnectionTimeoutError(system_address, timeout_seconds)


class DroneNotConnectedError(Exception):
    def __init__(self) -> None:
        super().__init__("Drone is not connected.")
