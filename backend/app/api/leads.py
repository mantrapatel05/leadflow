from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas.lead import (
    LeadCreate,
    LeadListResponse,
    LeadResponse,
)
from app.services.lead_service import (
    create_lead,
    get_lead_by_id,
    list_leads,
)

router = APIRouter(
    prefix="/leads",
    tags=["Leads"],
)


@router.post(
    "",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a lead",
)
async def create_lead_endpoint(
    lead_data: LeadCreate,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    lead, created = await create_lead(db, lead_data)
    if not created:
        response.status_code = status.HTTP_200_OK
    return lead


@router.get(
    "",
    response_model=LeadListResponse,
    summary="List leads",
)
async def list_leads_endpoint(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> LeadListResponse:
    leads, total = await list_leads(db, page, page_size)
    return LeadListResponse(
        leads=leads,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
    summary="Retrieve a lead",
)
async def get_lead_endpoint(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    lead = await get_lead_by_id(db, lead_id)
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return lead
