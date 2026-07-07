from __future__ import annotations

import asyncio
import math
from collections.abc import AsyncIterator
from typing import Any, Protocol

from app.models.drone import DroneTelemetrySnapshot
from app.services.drone_connection import DroneConnectionService, DroneNotConnectedError
from config import defaults
from logging.audit import audit_event
from logging.constants import AuditEvent
from logging.logger import get_logger

logger = get_logger(__name__)


class TelemetryPlugin(Protocol):
    def position(self) -> AsyncIterator[Any]:
        ...

    def velocity_ned(self) -> AsyncIterator[Any]:
        ...

    def heading(self) -> AsyncIterator[Any]:
        ...

    def battery(self) -> AsyncIterator[Any]:
        ...

    def gps_info(self) -> AsyncIterator[Any]:
        ...

    def flight_mode(self) -> AsyncIterator[Any]:
        ...


class MissionTelemetryPlugin(Protocol):
    def mission_progress(self) -> AsyncIterator[Any]:
        ...


class TelemetryService:
    def __init__(
        self,
        drone_connection: DroneConnectionService,
        timeout_seconds: float = defaults.DEFAULT_TELEMETRY_READ_TIMEOUT_SECONDS,
    ) -> None:
        self._drone_connection = drone_connection
        self._timeout_seconds = timeout_seconds

    async def get_snapshot(self) -> DroneTelemetrySnapshot:
        try:
            system = self._drone_connection.get_connected_system()
        except DroneNotConnectedError:
            logger.info("Telemetry requested while drone is disconnected.")
            return DroneTelemetrySnapshot(
                connected=False,
                message="Drone disconnected.",
            )

        telemetry: TelemetryPlugin = system.telemetry
        mission: MissionTelemetryPlugin = system.mission
        position, velocity, heading, battery, gps_info, flight_mode, progress = (
            await asyncio.gather(
                _read_first(telemetry.position(), self._timeout_seconds),
                _read_first(telemetry.velocity_ned(), self._timeout_seconds),
                _read_first(telemetry.heading(), self._timeout_seconds),
                _read_first(telemetry.battery(), self._timeout_seconds),
                _read_first(telemetry.gps_info(), self._timeout_seconds),
                _read_first(telemetry.flight_mode(), self._timeout_seconds),
                _read_first(mission.mission_progress(), self._timeout_seconds),
            )
        )

        return DroneTelemetrySnapshot(
            connected=True,
            latitude=_get(position, "latitude_deg"),
            longitude=_get(position, "longitude_deg"),
            altitude_meters=_get(position, "relative_altitude_m"),
            speed_meters_per_second=_ground_speed(velocity),
            heading_degrees=_get(heading, "heading_deg"),
            battery_percent=_battery_percent(battery),
            gps_satellites=_get(gps_info, "num_satellites"),
            gps_fix_type=_as_text(_get(gps_info, "fix_type")),
            flight_mode=_as_text(flight_mode),
            mission_current=_get(progress, "current"),
            mission_total=_get(progress, "total"),
            home_position_available=position is not None,
            message="Telemetry snapshot received.",
        )


async def _read_first(stream: AsyncIterator[Any], timeout_seconds: float) -> Any | None:
    try:
        async with asyncio.timeout(timeout_seconds):
            async for value in stream:
                return value
    except TimeoutError:
        audit_event(
            AuditEvent.TELEMETRY_TIMEOUT,
            "Telemetry stream read timed out.",
            level="WARNING",
        )
        return None

    return None


def _get(value: Any, attribute: str) -> Any | None:
    if value is None:
        return None

    return getattr(value, attribute, None)


def _ground_speed(velocity: Any | None) -> float | None:
    if velocity is None:
        return None

    north = getattr(velocity, "north_m_s", None)
    east = getattr(velocity, "east_m_s", None)
    if north is None or east is None:
        return None

    return math.sqrt((north * north) + (east * east))


def _battery_percent(battery: Any | None) -> float | None:
    remaining = _get(battery, "remaining_percent")
    if remaining is None:
        return None

    return remaining * 100


def _as_text(value: Any | None) -> str | None:
    if value is None:
        return None

    return str(value)
