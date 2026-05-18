from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_db_reports_disabled_without_mongodb_uri() -> None:
    with TestClient(app) as client:
        response = client.get("/health/db")

    assert response.status_code == 200
    body = response.json()
    assert body["mongo"] == "disabled"
    assert "MONGODB_URI" in body["detail"]
