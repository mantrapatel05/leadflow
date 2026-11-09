from typing import Any
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.webhook_event import WebhookEvent


async def store_leadgen_events(
    db: AsyncSession,
    payload: dict[str, Any],
) -> dict[str, int]:
    stored = 0
    duplicates = 0
    ignored = 0
    if payload.get("object") != "page":
        return {
            "stored": 0,
            "duplicates": 0,
            "ignored": 0,
        }
    entries = payload.get("entry", [])
    for entry in entries:
        page_id = str(entry.get("id", ""))
        for change in entry.get("changes", []):
            if change.get("field") != "leadgen":
                ignored += 1
                continue
            value = change.get("value", {})
            lead_id = value.get("leadgen_id")
            if not lead_id:
                ignored += 1
                continue
            event_key = f"leadgen:{lead_id}"
            form_id = value.get("form_id")
            event = WebhookEvent(
                event_key=event_key,
                object_type="page",
                field="leadgen",
                page_id=page_id,
                form_id=str(form_id) if form_id else None,
                meta_lead_id=str(lead_id),
                payload=value,
                status="pending",
            )
            db.add(event)
            try:
                await db.flush()
                stored += 1
            except IntegrityError:
                await db.rollback()
                duplicates += 1
    await db.commit()
    return {
        "stored": stored,
        "duplicates": duplicates,
        "ignored": ignored,
    }