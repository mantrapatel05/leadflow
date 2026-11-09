from fastapi.testclient import TestClient


def sample_lead():
    return {
        "meta_lead_id": "meta-test-1001",
        "page_id": "page-123",
        "form_id": "form-456",
        "ad_id": "ad-789",
        "full_name": "Test User",
        "email": "test@example.com",
        "phone_number": "+911234567890",
        "raw_payload": {
            "source": "test",
        },
    }


def test_create_lead(client: TestClient):
    response = client.post("/api/v1/leads", json=sample_lead())
    assert response.status_code == 201
    data = response.json()
    assert data["meta_lead_id"] == "meta-test-1001"
    assert data["full_name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert "raw_payload" not in data
    assert data["id"] == 1


def test_create_duplicate_lead(client: TestClient):
    payload = sample_lead()
    response1 = client.post("/api/v1/leads", json=payload)
    assert response1.status_code == 201
    response2 = client.post("/api/v1/leads", json=payload)
    assert response2.status_code == 200
    assert response1.json()["id"] == response2.json()["id"]


def test_list_leads(client: TestClient):
    client.post("/api/v1/leads", json=sample_lead())
    response = client.get("/api/v1/leads?page=1&page_size=20")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert len(data["leads"]) == 1


def test_retrieve_lead(client: TestClient):
    create_response = client.post("/api/v1/leads", json=sample_lead())
    lead_id = create_response.json()["id"]
    response = client.get(f"/api/v1/leads/{lead_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lead_id
    assert data["meta_lead_id"] == "meta-test-1001"


def test_retrieve_nonexistent_lead(client: TestClient):
    response = client.get("/api/v1/leads/999")
    assert response.status_code == 404


def test_invalid_email(client: TestClient):
    payload = sample_lead()
    payload["email"] = "not-an-email"
    response = client.post("/api/v1/leads", json=payload)
    assert response.status_code == 422


def test_invalid_pagination(client: TestClient):
    response = client.get("/api/v1/leads?page=0")
    assert response.status_code == 422
    response = client.get("/api/v1/leads?page_size=0")
    assert response.status_code == 422
    response = client.get("/api/v1/leads?page_size=101")
    assert response.status_code == 422
