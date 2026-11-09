from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LeadCreate(BaseModel):
    meta_lead_id: str = Field(min_length=1, max_length=255)
    page_id: str | None = Field(default=None, max_length=255)
    form_id: str | None = Field(default=None, max_length=255)
    ad_id: str | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None)
    phone_number: str | None = Field(default=None, max_length=50)
    raw_payload: dict | None = Field(default=None)


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meta_lead_id: str
    page_id: str | None
    form_id: str | None
    ad_id: str | None
    full_name: str | None
    email: str | None
    phone_number: str | None
    created_at: datetime
    updated_at: datetime


class LeadListResponse(BaseModel):
    leads: list[LeadResponse]
    total: int
    page: int
    page_size: int
