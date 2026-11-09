from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db

router = APIRouter(
    tags=["Health"],
)


@router.get("/health", summary="Check API health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "leadflow-api",
    }


@router.get("/ready", summary="Check application readiness")
async def readiness_check(
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    try:
        await db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not ready",
        )
    return {
        "status": "ready",
        "database": "connected",
    }
