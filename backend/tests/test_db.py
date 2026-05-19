from fastapi.testclient import TestClient

from app.main import app


def test_db_health_reports_disabled_without_mongodb_uri() -> None:
    with TestClient(app) as client:
        response = client.get("/db/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "disabled"
    assert "MONGODB_URI" in body["detail"]
