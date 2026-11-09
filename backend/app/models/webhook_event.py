from datetime import datetime
from typing import Any
from sqlalchemy import DateTime, Index, Integer, JSON, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    __table_args__ = (
        UniqueConstraint("event_key", name="uq_webhook_events_event_key"),
        Index("ix_webhook_events_status", "status"),
        Index("ix_webhook_events_received_at", "received_at"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    event_key: Mapped[str] = mapped_column(String(255), nullable=False)
    object_type: Mapped[str] = mapped_column(String(50), nullable=False)
    field: Mapped[str] = mapped_column(String(50), nullable=False)
    page_id: Mapped[str] = mapped_column(String(100), nullable=False)
    form_id: Mapped[str | None] = mapped_column(String(100))
    meta_lead_id: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    last_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )