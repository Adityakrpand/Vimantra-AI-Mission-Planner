import pytest

from app.services.drone_action import DroneActionService
from app.services.drone_connection import DroneConnectionService, DroneNotConnectedError


class FakeActionPlugin:
    def __init__(self) -> None:
        self.arm_calls = 0
        self.disarm_calls = 0

    async def arm(self) -> None:
        self.arm_calls += 1

    async def disarm(self) -> None:
        self.disarm_calls += 1


class FakeDroneSystem:
    def __init__(self) -> None:
        self.action = FakeActionPlugin()
        self.core = object()
        self.mission = FakeMissionPlugin()


class FakeMissionPlugin:
    def __init__(self) -> None:
        self.start_mission_calls = 0

    async def start_mission(self) -> None:
        self.start_mission_calls += 1


@pytest.mark.anyio
async def test_arm_calls_connected_drone_action_plugin() -> None:
    fake_system = FakeDroneSystem()
    service = DroneActionService(create_connected_connection(fake_system))

    status = await service.arm()

    assert status.completed is True
    assert status.action == "arm"
    assert status.message == "Drone armed."
    assert fake_system.action.arm_calls == 1


@pytest.mark.anyio
async def test_disarm_calls_connected_drone_action_plugin() -> None:
    fake_system = FakeDroneSystem()
    service = DroneActionService(create_connected_connection(fake_system))

    status = await service.disarm()

    assert status.completed is True
    assert status.action == "disarm"
    assert status.message == "Drone disarmed."
    assert fake_system.action.disarm_calls == 1


@pytest.mark.anyio
async def test_arm_requires_connected_drone() -> None:
    service = DroneActionService(DroneConnectionService())

    with pytest.raises(DroneNotConnectedError):
        await service.arm()


@pytest.mark.anyio
async def test_start_mission_calls_connected_drone_mission_plugin() -> None:
    fake_system = FakeDroneSystem()
    service = DroneActionService(create_connected_connection(fake_system))

    status = await service.start_mission()

    assert status.completed is True
    assert status.action == "start_mission"
    assert status.message == "Mission started."
    assert fake_system.mission.start_mission_calls == 1


def create_connected_connection(fake_system: FakeDroneSystem) -> DroneConnectionService:
    connection = DroneConnectionService(system_factory=lambda: fake_system)
    connection._system = fake_system
    connection._system_address = "udp://:14540"
    connection._connected = True
    return connection
