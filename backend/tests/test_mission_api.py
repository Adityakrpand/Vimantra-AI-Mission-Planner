from pathlib import Path
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_mission_storage
from app.main import create_app
from app.services.mission_storage import MissionStorage


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    storage = MissionStorage(tmp_path / "api-missions.sqlite")
    storage.initialize()
    app = create_app()
    app.dependency_overrides[get_mission_storage] = lambda: storage

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_and_get_mission(client: TestClient) -> None:
    create_response = client.post("/missions", json=create_payload())

    assert create_response.status_code == 201
    created = _data(create_response)
    assert created["id"] > 0
    assert created["name"] == "Survey Block A"
    assert [waypoint["sequence"] for waypoint in created["waypoints"]] == [1, 2]

    get_response = client.get(f"/missions/{created['id']}")

    assert get_response.status_code == 200
    assert _data(get_response)["name"] == "Survey Block A"


def test_list_missions(client: TestClient) -> None:
    client.post("/missions", json=create_payload(name="First Mission"))
    client.post("/missions", json=create_payload(name="Second Mission"))

    response = client.get("/missions")

    assert response.status_code == 200
    assert [mission["name"] for mission in _data(response)] == [
        "Second Mission",
        "First Mission",
    ]


def test_delete_mission(client: TestClient) -> None:
    create_response = client.post("/missions", json=create_payload())
    mission_id = _data(create_response)["id"]

    delete_response = client.delete(f"/missions/{mission_id}")
    get_response = client.get(f"/missions/{mission_id}")

    assert delete_response.status_code == 200
    assert _data(delete_response) == {"deleted": True}
    assert get_response.status_code == 404
    assert get_response.json()["success"] is False
    assert get_response.json()["error"]["message"] == f"Mission {mission_id} was not found."


def test_create_mission_rejects_invalid_payload(client: TestClient) -> None:
    response = client.post(
        "/missions",
        json={
            "name": "",
            "waypoints": [],
        },
    )

    assert response.status_code == 422
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_get_missing_mission_returns_404(client: TestClient) -> None:
    response = client.get("/missions/404")

    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert response.json()["error"]["message"] == "Mission 404 was not found."


def _data(response):
    body = response.json()
    assert body["success"] is True
    assert body["request_id"]
    assert body["error"] is None
    return body["data"]


def create_payload(name: str = "Survey Block A") -> dict[str, object]:
    return {
        "name": name,
        "waypoints": [
            {
                "sequence": 4,
                "latitude": 19.076,
                "longitude": 72.8777,
                "altitude_meters": 80,
                "speed_meters_per_second": 8,
            },
            {
                "sequence": 9,
                "latitude": 19.0821,
                "longitude": 72.8903,
                "altitude_meters": 90,
                "speed_meters_per_second": 9,
            },
        ],
    }
