from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.analytics_schema import AnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    range: str = Query("all", pattern="^(7d|30d|90d|1y|all)$"),
    project_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AnalyticsResponse:
    """
    Get user-scoped deterministic analytics.
    Exclusively derives metrics from persisted projects, ideas, evaluations, and reports.
    """
    return await AnalyticsService.get_user_analytics(
        db=db,
        user_id=current_user.id,
        time_range=range,
        project_id=project_id
    )
