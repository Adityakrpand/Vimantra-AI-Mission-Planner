from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.main import create_app


def test_success_response_includes_generated_request_id() -> None:
    client = TestClient(create_app())

    response = client.get("/health")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["request_id"]
    assert response.headers["x-request-id"] == body["request_id"]
    assert body["data"]["status"] == "ok"


def test_success_response_uses_incoming_request_id() -> None:
    client = TestClient(create_app())

    response = client.get("/health", headers={"x-request-id": "test-request-123"})

    assert response.status_code == 200
    assert response.json()["request_id"] == "test-request-123"
    assert response.headers["x-request-id"] == "test-request-123"


def test_unknown_route_returns_standard_404_response() -> None:
    client = TestClient(create_app())

    response = client.get("/missing-route")
    body = response.json()

    assert response.status_code == 404
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["request_id"]


def test_request_validation_returns_standard_422_response() -> None:
    client = TestClient(create_app())

    response = client.post("/missions", json={"name": "", "waypoints": []})
    body = response.json()

    assert response.status_code == 422
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(body["error"]["details"], list)


def test_unhandled_exception_returns_standard_500_response() -> None:
    app = create_app()
    router = APIRouter()

    @router.get("/boom")
    def boom() -> None:
        raise RuntimeError("boom")

    app.include_router(router)
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/boom")
    body = response.json()

    assert response.status_code == 500
    assert body["success"] is False
    assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert body["error"]["message"] == "An unexpected server error occurred."
    assert body["request_id"]
