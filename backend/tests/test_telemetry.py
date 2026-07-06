from dataclasses import dataclass
from enum import Enum

import pytest

from app.services.drone_connection import DroneConnectionService
from app.services.telemetry import TelemetryService


class FakeFlightMode(Enum):
    HOLD = "HOLD"


@dataclass(frozen=True)
class FakePosition:
    latitude_deg: float
    longitude_deg: float
    relative_altitude_m: float


@dataclass(frozen=True)
class FakeVelocity:
    north_m_s: float
    east_m_s: float


@dataclass(frozen=True)
class FakeHeading:
    heading_deg: float


@dataclass(frozen=True)
class FakeBattery:
    remaining_percent: float


@dataclass(frozen=True)
class FakeGpsInfo:
    fix_type: str


@dataclass(frozen=True)
class FakeMissionProgress:
    current: int
    total: int


class FakeTelemetryPlugin:
    async def position(self):
        yield FakePosition(19.076, 72.8777, 80)

    async def velocity_ned(self):
        yield FakeVelocity(3, 4)

    async def heading(self):
        yield FakeHeading(125)

    async def battery(self):
        yield FakeBattery(0.76)

    async def gps_info(self):
        yield FakeGpsInfo("FIX_3D")

    async def flight_mode(self):
        yield FakeFlightMode.HOLD


class FakeMissionPlugin:
    async def mission_progress(self):
        yield FakeMissionProgress(2, 5)


class FakeDroneSystem:
    def __init__(self) -> None:
        self.action = object()
        self.core = object()
        self.mission = FakeMissionPlugin()
        self.telemetry = FakeTelemetryPlugin()


@pytest.mark.anyio
async def test_telemetry_snapshot_returns_disconnected_state() -> None:
    snapshot = await TelemetryService(DroneConnectionService()).get_snapshot()

    assert snapshot.connected is False
    assert snapshot.message == "Drone disconnected."
    assert snapshot.latitude is None


@pytest.mark.anyio
async def test_telemetry_snapshot_reads_connected_drone_streams() -> None:
    connection = create_connected_connection(FakeDroneSystem())

    snapshot = await TelemetryService(connection).get_snapshot()

    assert snapshot.connected is True
    assert snapshot.latitude == 19.076
    assert snapshot.longitude == 72.8777
    assert snapshot.altitude_meters == 80
    assert snapshot.speed_meters_per_second == 5
    assert snapshot.heading_degrees == 125
    assert snapshot.battery_percent == 76
    assert snapshot.gps_fix_type == "FIX_3D"
    assert snapshot.flight_mode == "FakeFlightMode.HOLD"
    assert snapshot.mission_current == 2
    assert snapshot.mission_total == 5


def create_connected_connection(fake_system: FakeDroneSystem) -> DroneConnectionService:
    connection = DroneConnectionService(system_factory=lambda: fake_system)
    connection._system = fake_system
    connection._system_address = "udp://:14540"
    connection._connected = True
    return connection
