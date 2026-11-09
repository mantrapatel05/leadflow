from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["project"] == "LeadFlow"
    assert data["status"] == "running"


def test_health_endpoint():
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "leadflow-api"


def test_health_response_structure():
    response = client.get("/api/v1/health")

    data = response.json()

    assert set(data.keys()) == {
        "status",
        "service",
    }
