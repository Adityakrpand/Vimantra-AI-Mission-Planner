from pathlib import Path

import pytest

from app.models.mission import MissionCreate, Waypoint
from app.services.drone_connection import DroneConnectionService
from app.services.mission_storage import MissionStorage
from app.services.mission_upload import MissionUploadService
from preflight.exceptions import PreFlightCheckFailedError


class FakeMissionPlugin:
    def __init__(self) -> None:
        self.uploaded_plan = None

    async def upload_mission(self, mission_plan) -> None:
        self.uploaded_plan = mission_plan

    async def mission_progress(self):
        yield FakeMissionProgress()


class FakeDroneSystem:
    def __init__(self) -> None:
        self.mission = FakeMissionPlugin()
        self.core = object()
        self.telemetry = FakeTelemetryPlugin()


class FakeTelemetryPlugin:
    async def position(self):
        yield FakePosition()

    async def velocity_ned(self):
        yield FakeVelocity()

    async def heading(self):
        yield FakeHeading()

    async def battery(self):
        yield FakeBattery()

    async def gps_info(self):
        yield FakeGpsInfo()

    async def flight_mode(self):
        yield "HOLD"


class FakePosition:
    latitude_deg = 19.076
    longitude_deg = 72.8777
    relative_altitude_m = 80


class FakeVelocity:
    north_m_s = 0
    east_m_s = 6


class FakeHeading:
    heading_deg = 90


class FakeBattery:
    remaining_percent = 0.8


class FakeGpsInfo:
    fix_type = "FIX_3D"
    num_satellites = 10


class FakeMissionProgress:
    current = 0
    total = 2


@pytest.mark.anyio
async def test_upload_mission_converts_waypoints_to_mavsdk_plan(
    tmp_path: Path,
) -> None:
    storage = create_storage(tmp_path)
    mission = storage.save_mission(create_mission())
    fake_system = FakeDroneSystem()
    drone_connection = DroneConnectionService(system_factory=lambda: fake_system)
    drone_connection._system = fake_system
    drone_connection._system_address = "udp://:14540"
    drone_connection._connected = True
    service = MissionUploadService(storage, drone_connection)

    status = await service.upload_mission(mission.id)

    assert status.uploaded is True
    assert status.mission_id == mission.id
    assert drone_connection.loaded_mission_id() == mission.id
    assert fake_system.mission.uploaded_plan is not None
    assert len(fake_system.mission.uploaded_plan.mission_items) == 2
    assert fake_system.mission.uploaded_plan.mission_items[0].latitude_deg == 19.076
    assert (
        fake_system.mission.uploaded_plan.mission_items[0].relative_altitude_m
        == 80
    )


@pytest.mark.anyio
async def test_upload_requires_connected_drone(tmp_path: Path) -> None:
    storage = create_storage(tmp_path)
    mission = storage.save_mission(create_mission())
    service = MissionUploadService(storage, DroneConnectionService())

    with pytest.raises(PreFlightCheckFailedError):
        await service.upload_mission(mission.id)


def create_storage(tmp_path: Path) -> MissionStorage:
    storage = MissionStorage(tmp_path / "upload.sqlite")
    storage.initialize()
    return storage


def create_mission() -> MissionCreate:
    return MissionCreate(
        name="Upload Mission",
        waypoints=[
            Waypoint(
                sequence=1,
                latitude=19.076,
                longitude=72.8777,
                altitude_meters=80,
                speed_meters_per_second=8,
            ),
            Waypoint(
                sequence=2,
                latitude=19.0821,
                longitude=72.8903,
                altitude_meters=90,
                speed_meters_per_second=9,
            ),
        ],
    )
