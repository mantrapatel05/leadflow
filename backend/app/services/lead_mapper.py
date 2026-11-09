from typing import Any
from app.schemas.lead import LeadCreate


def normalize_field_data(
    field_data: list[dict[str, Any]],
) -> dict[str, str]:
    normalized = {}
    for field in field_data:
        name = field.get("name")
        values = field.get("values", [])
        if name and values:
            normalized[name] = str(values[0])
    return normalized


def map_meta_lead_to_create(
    meta_data: dict[str, Any],
    page_id: str,
    form_id: str | None,
    ad_id: str | None,
) -> LeadCreate:
    fields = normalize_field_data(
        meta_data.get("field_data", [])
    )
    full_name = fields.get("full_name")
    if not full_name:
        first_name = fields.get("first_name", "")
        last_name = fields.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip() or None
    return LeadCreate(
        meta_lead_id=str(meta_data.get("id", "")),
        page_id=page_id,
        form_id=form_id,
        ad_id=ad_id,
        full_name=full_name,
        email=fields.get("email"),
        phone_number=fields.get("phone_number"),
        raw_payload=meta_data,
    )