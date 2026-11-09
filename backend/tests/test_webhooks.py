import hashlib
import hmac
import json
import pytest
from fastapi.testclient import TestClient
from app.core.config import get_settings
from app.main import app


@pytest.fixture
def configured_client(monkeypatch, tmp_path):
    monkeypatch.setenv("META_VERIFY_TOKEN", "test-verify-token")
    monkeypatch.setenv("META_APP_SECRET", "test-app-secret")
    get_settings.cache_clear()

    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )
    from app.database.base import Base
    from app.database.session import get_db

    database_path = tmp_path / "test_webhook_leadflow.db"
    database_url = f"sqlite+aiosqlite:///{database_path.as_posix()}"

    async def override_get_db():
        test_engine = create_async_engine(database_url)
        async with test_engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        test_session_factory = async_sessionmaker(
            bind=test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def sign_payload(payload: bytes) -> str:
    digest = hmac.new(
        b"test-app-secret",
        payload,
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"


def test_meta_webhook_verification(configured_client):
    response = configured_client.get(
        "/api/v1/webhooks/meta",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "test-verify-token",
            "hub.challenge": "challenge-123",
        },
    )
    assert response.status_code == 200
    assert response.text == "challenge-123"


def test_meta_webhook_verification_wrong_token(configured_client):
    response = configured_client.get(
        "/api/v1/webhooks/meta",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong-token",
            "hub.challenge": "challenge-123",
        },
    )
    assert response.status_code == 403


def test_meta_webhook_verification_no_challenge(configured_client):
    response = configured_client.get(
        "/api/v1/webhooks/meta",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "test-verify-token",
        },
    )
    assert response.status_code == 403


def test_meta_webhook_post_valid(configured_client):
    payload = {
        "object": "page",
        "entry": [
            {
                "id": "page-123",
                "time": 1234567890,
                "changes": [
                    {
                        "field": "leadgen",
                        "value": {
                            "leadgen_id": "lead-456",
                            "form_id": "form-789",
                            "page_id": "page-123",
                            "ad_id": "ad-101",
                            "created_time": "2026-01-01T00:00:00+00:00",
                        },
                    }
                ],
            }
        ],
    }
    body = json.dumps(payload).encode()
    signature = sign_payload(body)
    response = configured_client.post(
        "/api/v1/webhooks/meta",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": signature,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["stored"] == 1
    assert data["duplicates"] == 0


def test_meta_webhook_post_invalid_signature(configured_client):
    payload = {
        "object": "page",
        "entry": [
            {
                "id": "page-123",
                "changes": [
                    {
                        "field": "leadgen",
                        "value": {"leadgen_id": "lead-999"},
                    }
                ],
            }
        ],
    }
    body = json.dumps(payload).encode()
    response = configured_client.post(
        "/api/v1/webhooks/meta",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=invalidsignature",
        },
    )
    assert response.status_code == 401


def test_meta_webhook_post_duplicate(configured_client):
    payload = {
        "object": "page",
        "entry": [
            {
                "id": "page-123",
                "changes": [
                    {
                        "field": "leadgen",
                        "value": {"leadgen_id": "lead-dup"},
                    }
                ],
            }
        ],
    }
    body = json.dumps(payload).encode()
    signature = sign_payload(body)
    response1 = configured_client.post(
        "/api/v1/webhooks/meta",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": signature,
        },
    )
    assert response1.status_code == 200
    assert response1.json()["stored"] == 1

    response2 = configured_client.post(
        "/api/v1/webhooks/meta",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": signature,
        },
    )
    assert response2.status_code == 200
    assert response2.json()["stored"] == 0
    assert response2.json()["duplicates"] == 1


def test_meta_webhook_post_non_leadgen(configured_client):
    payload = {
        "object": "page",
        "entry": [
            {
                "id": "page-123",
                "changes": [
                    {
                        "field": "feed",
                        "value": {"item": "post"},
                    }
                ],
            }
        ],
    }
    body = json.dumps(payload).encode()
    signature = sign_payload(body)
    response = configured_client.post(
        "/api/v1/webhooks/meta",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": signature,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["stored"] == 0
    assert data["ignored"] == 1