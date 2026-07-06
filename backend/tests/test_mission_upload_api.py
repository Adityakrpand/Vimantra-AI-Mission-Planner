from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_drone_connection_service, get_mission_storage
from app.main import create_app
from app.services.drone_connection import DroneConnectionService
from app.services.mission_storage import MissionStorage


class FakeMissionPlugin:
    def __init__(self) -> None:
        self.upload_count = 0

    async def upload_mission(self, mission_plan) -> None:
        self.upload_count = len(mission_plan.mission_items)


class FakeDroneSystem:
    def __init__(self) -> None:
        self.mission = FakeMissionPlugin()
        self.core = object()


@pytest.fixture
def api_context(
    tmp_path: Path,
) -> Iterator[tuple[TestClient, FakeDroneSystem, DroneConnectionService]]:
    storage = MissionStorage(tmp_path / "api-upload.sqlite")
    storage.initialize()
    fake_system = FakeDroneSystem()
    drone_connection = DroneConnectionService(system_factory=lambda: fake_system)
    app = create_app()
    app.dependency_overrides[get_mission_storage] = lambda: storage
    app.dependency_overrides[get_drone_connection_service] = lambda: drone_connection

    with TestClient(app) as test_client:
        yield test_client, fake_system, drone_connection

    app.dependency_overrides.clear()


def test_upload_mission_returns_conflict_when_drone_disconnected(
    api_context: tuple[TestClient, FakeDroneSystem, DroneConnectionService],
) -> None:
    client, _, _ = api_context
    mission_id = client.post("/missions", json=create_payload()).json()["id"]

    response = client.post(f"/missions/{mission_id}/upload")

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Connect to PX4 SITL before uploading a mission."
    }


def test_upload_mission_calls_connected_drone_mission_plugin(
    api_context: tuple[TestClient, FakeDroneSystem, DroneConnectionService],
) -> None:
    client, fake_system, drone_connection = api_context
    drone_connection._system = fake_system
    drone_connection._system_address = "udp://:14540"
    drone_connection._connected = True
    mission_id = client.post("/missions", json=create_payload()).json()["id"]

    response = client.post(f"/missions/{mission_id}/upload")

    assert response.status_code == 200
    assert response.json() == {
        "mission_id": mission_id,
        "uploaded": True,
        "waypoint_count": 2,
        "message": "Uploaded mission Upload API Mission.",
    }
    assert fake_system.mission.upload_count == 2


def create_payload() -> dict[str, object]:
    return {
        "name": "Upload API Mission",
        "waypoints": [
            {
                "sequence": 1,
                "latitude": 19.076,
                "longitude": 72.8777,
                "altitude_meters": 80,
                "speed_meters_per_second": 8,
            },
            {
                "sequence": 2,
                "latitude": 19.0821,
                "longitude": 72.8903,
                "altitude_meters": 90,
                "speed_meters_per_second": 9,
            },
        ],
    }
