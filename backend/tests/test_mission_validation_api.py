from fastapi.testclient import TestClient

from app.main import create_app


def test_validate_mission_returns_structured_result() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/missions/validate",
        json={
            "name": "API Validation Mission",
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
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["request_id"]
    assert body["data"]["valid"] is True
    assert body["data"]["errors"] == []
    assert body["data"]["statistics"]["waypoints"] == 2
    assert body["data"]["statistics"]["distance"] > 0


def test_validate_mission_returns_errors_instead_of_plain_text() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/missions/validate",
        json={
            "name": "",
            "waypoints": [
                {
                    "sequence": 1,
                    "latitude": None,
                    "longitude": 72.8777,
                    "altitude_meters": 4,
                    "speed_meters_per_second": 20,
                }
            ],
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["valid"] is False
    assert isinstance(body["data"]["errors"], list)
    assert {error["code"] for error in body["data"]["errors"]} >= {
        "MISSION_NAME_REQUIRED",
        "TOO_FEW_WAYPOINTS",
        "LATITUDE_REQUIRED",
        "ALTITUDE_TOO_LOW",
        "SPEED_TOO_HIGH",
    }
