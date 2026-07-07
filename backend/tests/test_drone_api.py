from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_drone_connection_service, get_mission_storage
from app.main import create_app
from app.services.mission_storage import MissionStorage
from app.services.drone_connection import DroneConnectionService


class FakeConnectionState:
    def __init__(self, is_connected: bool) -> None:
        self.is_connected = is_connected


class FakeCoreTelemetry:
    def __init__(self, states: list[FakeConnectionState]) -> None:
        self._states = states

    async def connection_state(self) -> AsyncIterator[FakeConnectionState]:
        for state in self._states:
            yield state


class FakeDroneSystem:
    def __init__(self, states: list[FakeConnectionState]) -> None:
        self.action = FakeActionPlugin()
        self.core = FakeCoreTelemetry(states)
        self.mission = FakeMissionPlugin()
        self.telemetry = FakeTelemetryPlugin()

    async def connect(self, system_address: str | None = None) -> None:
        return None


class FakeActionPlugin:
    def __init__(self) -> None:
        self.arm_calls = 0
        self.disarm_calls = 0

    async def arm(self) -> None:
        self.arm_calls += 1

    async def disarm(self) -> None:
        self.disarm_calls += 1


class FakeMissionPlugin:
    def __init__(self) -> None:
        self.start_mission_calls = 0

    async def start_mission(self) -> None:
        self.start_mission_calls += 1

    async def mission_progress(self):
        yield FakeMissionProgress(1, 3)


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
    remaining_percent = 0.5


class FakeGpsInfo:
    fix_type = "FIX_3D"
    num_satellites = 10


class FakeMissionProgress:
    def __init__(self, current: int, total: int) -> None:
        self.current = current
        self.total = total


@pytest.fixture
def client(tmp_path) -> Iterator[tuple[TestClient, DroneConnectionService, MissionStorage]]:
    service = DroneConnectionService(
        system_factory=lambda: FakeDroneSystem([FakeConnectionState(True)])
    )
    storage = MissionStorage(tmp_path / "drone-api.sqlite")
    storage.initialize()
    app = create_app()
    app.dependency_overrides[get_drone_connection_service] = lambda: service
    app.dependency_overrides[get_mission_storage] = lambda: storage

    with TestClient(app) as test_client:
        yield test_client, service, storage

    app.dependency_overrides.clear()


def test_drone_status_defaults_to_disconnected(client) -> None:
    client, _, _ = client
    response = client.get("/drone/status")

    assert response.status_code == 200
    assert _data(response) == {
        "connected": False,
        "system_address": None,
        "message": "Drone disconnected.",
    }


def test_drone_telemetry_defaults_to_disconnected(client) -> None:
    client, _, _ = client
    response = client.get("/drone/telemetry")

    assert response.status_code == 200
    assert _data(response)["connected"] is False
    assert _data(response)["message"] == "Drone disconnected."


def test_connect_and_disconnect_drone(client) -> None:
    client, _, _ = client
    connect_response = client.post(
        "/drone/connect",
        json={"system_address": "udp://:14540", "timeout_seconds": 1},
    )
    status_response = client.get("/drone/status")
    disconnect_response = client.post("/drone/disconnect")

    assert connect_response.status_code == 200
    assert _data(connect_response)["connected"] is True
    assert _data(status_response)["system_address"] == "udp://:14540"
    assert _data(disconnect_response) == {
        "connected": False,
        "system_address": None,
        "message": "Drone connection cleared.",
    }


def test_arm_and_disarm_return_conflict_when_disconnected(
    client,
) -> None:
    client, _, _ = client
    arm_response = client.post("/drone/arm")
    disarm_response = client.post("/drone/disarm")
    start_response = client.post("/drone/start-mission")

    assert arm_response.status_code == 409
    assert arm_response.json()["success"] is False
    assert arm_response.json()["error"]["code"] == "CONFLICT"
    assert arm_response.json()["error"]["message"] == (
        "Connect to PX4 SITL before sending drone actions."
    )
    assert disarm_response.status_code == 409
    assert start_response.status_code == 409


def test_arm_and_disarm_connected_drone(client) -> None:
    client, _, _ = client
    client.post(
        "/drone/connect",
        json={"system_address": "udp://:14540", "timeout_seconds": 1},
    )

    arm_response = client.post("/drone/arm")
    disarm_response = client.post("/drone/disarm")

    assert arm_response.status_code == 200
    assert _data(arm_response) == {
        "completed": True,
        "action": "arm",
        "message": "Drone armed.",
    }
    assert disarm_response.status_code == 200
    assert _data(disarm_response) == {
        "completed": True,
        "action": "disarm",
        "message": "Drone disarmed.",
    }


def test_start_mission_requires_uploaded_mission(client) -> None:
    client, _, _ = client
    client.post(
        "/drone/connect",
        json={"system_address": "udp://:14540", "timeout_seconds": 1},
    )

    response = client.post("/drone/start-mission")

    assert response.status_code == 409
    assert response.json()["error"]["message"] == "Upload a mission before starting."


def test_start_mission_connected_drone(client) -> None:
    client, service, storage = client
    mission = storage.save_mission(create_payload_model())
    service.mark_mission_loaded(mission.id)
    client.post(
        "/drone/connect",
        json={"system_address": "udp://:14540", "timeout_seconds": 1},
    )

    response = client.post("/drone/start-mission")

    assert response.status_code == 200
    assert _data(response) == {
        "completed": True,
        "action": "start_mission",
        "message": "Mission started.",
    }


def test_drone_telemetry_connected_drone(client) -> None:
    client, _, _ = client
    client.post(
        "/drone/connect",
        json={"system_address": "udp://:14540", "timeout_seconds": 1},
    )

    response = client.get("/drone/telemetry")

    assert response.status_code == 200
    assert _data(response)["connected"] is True
    assert _data(response)["latitude"] == 19.076
    assert _data(response)["speed_meters_per_second"] == 6
    assert _data(response)["mission_current"] == 1
    assert _data(response)["mission_total"] == 3


def create_payload_model():
    from app.models.mission import MissionCreate, Waypoint

    return MissionCreate(
        name="Loaded Drone Mission",
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


def _data(response):
    body = response.json()
    assert body["success"] is True
    assert body["request_id"]
    assert body["error"] is None
    return body["data"]
