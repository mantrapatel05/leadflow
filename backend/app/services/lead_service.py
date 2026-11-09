from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.lead import Lead
from app.schemas.lead import LeadCreate


async def create_lead(
    db: AsyncSession,
    lead_data: LeadCreate,
) -> tuple[Lead, bool]:
    lead = Lead(**lead_data.model_dump())
    db.add(lead)
    try:
        await db.commit()
        await db.refresh(lead)
        return lead, True
    except IntegrityError:
        await db.rollback()
        result = await db.execute(select(Lead).where(Lead.meta_lead_id == lead_data.meta_lead_id))
        existing = result.scalar_one_or_none()
        if existing is not None:
            return existing, False
        raise


async def get_lead_by_id(db: AsyncSession, lead_id: int) -> Lead | None:
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    return result.scalar_one_or_none()


async def list_leads(db: AsyncSession, page: int, page_size: int) -> tuple[list[Lead], int]:
    count_result = await db.execute(select(func.count(Lead.id)))
    total = count_result.scalar_one()
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Lead)
        .offset(offset)
        .limit(page_size)
        .order_by(Lead.created_at.desc())
    )
    leads = list(result.scalars().all())
    return leads, total
