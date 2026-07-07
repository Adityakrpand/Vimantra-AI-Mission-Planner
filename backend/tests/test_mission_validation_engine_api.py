from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_mission_storage
from app.main import create_app
from app.services.mission_storage import MissionStorage


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    storage = MissionStorage(tmp_path / "validation-api.sqlite")
    storage.initialize()
    app = create_app()
    app.dependency_overrides[get_mission_storage] = lambda: storage

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_get_mission_validation(client: TestClient) -> None:
    mission_id = _data(client.post("/missions", json=create_payload()))["id"]

    response = client.get(f"/missions/{mission_id}/validation")
    data = _data(response)

    assert response.status_code == 200
    assert data["status"] == "ready"
    assert data["score"] == 100
    assert data["summary"]["passed"] is True
    assert data["checks"]


def test_get_missing_mission_validation_returns_404(client: TestClient) -> None:
    response = client.get("/missions/404/validation")

    assert response.status_code == 404
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "NOT_FOUND"


def create_payload() -> dict[str, object]:
    return {
        "name": "Validation API Mission",
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


def _data(response):
    body = response.json()
    assert body["success"] is True
    assert body["request_id"]
    assert body["error"] is None
    return body["data"]
