from fastapi.testclient import TestClient

from app.main import create_app


def test_health_check_returns_service_status() -> None:
  client = TestClient(create_app())

  response = client.get("/health")
  body = response.json()

  assert response.status_code == 200
  assert body["success"] is True
  assert body["request_id"]
  assert body["error"] is None
  assert body["data"] == {
    "status": "ok",
    "service": "vimantra-backend",
  }
