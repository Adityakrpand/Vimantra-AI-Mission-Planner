from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_mission_storage
from app.main import create_app
from app.services.mission_storage import MissionStorage


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    storage = MissionStorage(tmp_path / "analytics-api.sqlite")
    storage.initialize()
    app = create_app()
    app.dependency_overrides[get_mission_storage] = lambda: storage

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_get_mission_analytics(client: TestClient) -> None:
    mission_id = _data(client.post("/missions", json=create_payload()))["id"]

    response = client.get(f"/missions/{mission_id}/analytics")
    data = _data(response)

    assert response.status_code == 200
    assert data["summary"]["waypoint_count"] == 3
    assert data["summary"]["distance_meters"] > 0
    assert data["statistics"]["maximum_altitude_meters"] == 90
    assert isinstance(data["warnings"], list)


def create_payload() -> dict[str, object]:
    return {
        "name": "Analytics API Mission",
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
            {
                "sequence": 3,
                "latitude": 19.0664,
                "longitude": 72.9008,
                "altitude_meters": 70,
                "speed_meters_per_second": 7,
            },
        ],
    }


def _data(response):
    body = response.json()
    assert body["success"] is True
    assert body["request_id"]
    assert body["error"] is None
    return body["data"]
