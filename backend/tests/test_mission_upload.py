from pathlib import Path

import pytest

from app.models.mission import MissionCreate, Waypoint
from app.services.drone_connection import DroneConnectionService, DroneNotConnectedError
from app.services.mission_storage import MissionStorage
from app.services.mission_upload import MissionUploadService


class FakeMissionPlugin:
    def __init__(self) -> None:
        self.uploaded_plan = None

    async def upload_mission(self, mission_plan) -> None:
        self.uploaded_plan = mission_plan


class FakeDroneSystem:
    def __init__(self) -> None:
        self.mission = FakeMissionPlugin()
        self.core = object()


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

    with pytest.raises(DroneNotConnectedError):
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
