from typing import Optional, Dict, Any
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


# ==============================================================================
# FEATURE 3: AI CREDIT & TOKEN GAUGE
# ==============================================================================

@router.get("/ai/usage-gauge", summary="Fetch real-time AI token consumption, request counts, and cost estimates")
async def get_ai_usage_gauge(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    return await AnalyticsService.get_ai_usage_gauge(db, current_user.id)


# ==============================================================================
# FEATURE 4: RECENT ACTIVITY FEED
# ==============================================================================

@router.get("/activity", summary="Fetch paginated real-time user activity feed")
async def get_recent_activity(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    return await AnalyticsService.get_recent_activity(db, current_user.id, page=page, limit=limit)


# ==============================================================================
# FEATURE 13: VENTURE MATRIX (2D VISUALIZATION)
# ==============================================================================

@router.get("/venture-matrix", summary="Fetch 2D Attractiveness vs Risk plot coordinates for all user ventures")
async def get_venture_matrix(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    return await AnalyticsService.get_venture_matrix(db, current_user.id)


# ==============================================================================
# FEATURE 52: AI / PROVIDER PERFORMANCE TELEMETRY
# ==============================================================================

@router.get("/ai/telemetry", summary="Fetch provider-level latency, success rates, and token consumption")
async def get_ai_telemetry(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    return await AnalyticsService.get_ai_telemetry(db, current_user.id)


# ==============================================================================
# FEATURE 53: CACHE HIT-RATE / LATENCY TELEMETRY
# ==============================================================================

@router.get("/ai/cache-telemetry", summary="Fetch cache hit rate, cold vs warm latencies, and token cost savings")
async def get_cache_telemetry(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    return AnalyticsService.get_cache_telemetry()
