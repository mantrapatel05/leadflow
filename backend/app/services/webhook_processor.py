from datetime import datetime, timezone
from sqlalchemy import select
from app.database.session import SessionFactory
from app.models.webhook_event import WebhookEvent
from app.services.lead_mapper import map_meta_lead_to_create
from app.services.lead_service import create_lead
from app.services.meta_client import MetaClient

MAX_RETRIES = 5


async def _mark_event_failure(db, event: WebhookEvent) -> None:
    event.retry_count += 1
    event.last_attempt_at = datetime.now(timezone.utc)
    if event.retry_count >= MAX_RETRIES:
        event.status = "failed"
    else:
        event.status = "pending"


async def process_webhook_event(event_id: int) -> bool:
    # Phase 1: Read the event, then close the session before
    # making an external network request.
    async with SessionFactory() as db:
        event = await db.get(WebhookEvent, event_id)
        if event is None or event.status != "pending":
            return False
        page_id = event.page_id
        form_id = event.form_id
        meta_lead_id = event.meta_lead_id
        payload = event.payload

    ad_id = payload.get("ad_id") if isinstance(payload, dict) else None

    # Phase 2: External Graph API call — no DB transaction held open.
    try:
        client = MetaClient()
        meta_data = await client.get_lead(meta_lead_id)
        lead_data = map_meta_lead_to_create(
            meta_data=meta_data,
            page_id=page_id,
            form_id=form_id,
            ad_id=ad_id,
        )
    except Exception:
        async with SessionFactory() as db:
            event = await db.get(WebhookEvent, event_id)
            if event:
                await _mark_event_failure(db, event)
                await db.commit()
        return False

    # Phase 3: Persist lead and mark the event as processed.
    try:
        async with SessionFactory() as db:
            await create_lead(db, lead_data)
            event = await db.get(WebhookEvent, event_id)
            if event:
                event.status = "processed"
                event.retry_count = 0
                await db.commit()
        return True
    except Exception:
        async with SessionFactory() as db:
            event = await db.get(WebhookEvent, event_id)
            if event:
                await _mark_event_failure(db, event)
                await db.commit()
        return False


async def process_pending_webhooks(batch_size: int = 20) -> dict:
    async with SessionFactory() as db:
        result = await db.execute(
            select(WebhookEvent)
            .where(WebhookEvent.status == "pending")
            .order_by(WebhookEvent.received_at.asc())
            .limit(batch_size)
        )
        events = list(result.scalars().all())

    attempted = 0
    processed = 0
    unsuccessful = 0

    for event in events:
        attempted += 1
        success = await process_webhook_event(event.id)
        if success:
            processed += 1
        else:
            unsuccessful += 1

    return {
        "attempted": attempted,
        "processed": processed,
        "unsuccessful": unsuccessful,
    }