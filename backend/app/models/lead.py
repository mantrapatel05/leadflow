from datetime import datetime
from sqlalchemy import (
    DateTime,
    Index,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class Lead(Base):
    __tablename__ = "leads"
    __table_args__ = (
        UniqueConstraint(
            "meta_lead_id",
            name="uq_leads_meta_lead_id",
        ),
        Index("ix_leads_created_at", "created_at"),
        Index("ix_leads_email", "email"),
    )
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    meta_lead_id: Mapped[str] = mapped_column(String(255), nullable=False)
    page_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    form_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ad_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
