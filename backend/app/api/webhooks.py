import json
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.core.security import verify_meta_signature
from app.database.session import get_db
from app.services.webhook_service import store_leadgen_events

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.get("/meta", response_class=PlainTextResponse)
async def verify_meta_webhook(
    mode: str | None = Query(default=None, alias="hub.mode"),
    token: str | None = Query(default=None, alias="hub.verify_token"),
    challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    settings = get_settings()
    if (
        mode == "subscribe"
        and token
        and settings.meta_verify_token
        and token == settings.meta_verify_token
        and challenge is not None
    ):
        return challenge
    raise HTTPException(
        status_code=403,
        detail="Webhook verification failed",
    )


@router.post("/meta")
async def receive_meta_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None, alias="X-Hub-Signature-256"),
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    raw_body = await request.body()
    if not verify_meta_signature(raw_body, x_hub_signature_256, settings.meta_app_secret):
        raise HTTPException(
            status_code=401,
            detail="Invalid signature",
        )
    payload = json.loads(raw_body)
    result = await store_leadgen_events(db, payload)
    return {"status": "ok", **result}