from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "LeadFlow"
    assert data["status"] == "running"


def test_health_endpoint(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "leadflow-api"


def test_health_response_structure(client: TestClient):
    response = client.get("/api/v1/health")
    data = response.json()
    assert set(data.keys()) == {
        "status",
        "service",
    }
