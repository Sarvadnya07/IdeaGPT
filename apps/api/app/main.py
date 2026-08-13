from fastapi import FastAPI, Depends, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func

from app.core.config import settings
from app.core.logging import RequestLoggingMiddleware
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
from app.db.session import get_db
from app.models.ai_task import AiTask
from app.api.routes import project_routes, user_routes, idea_routes, evaluation_routes, roadmap_routes, ai_routes, analytics_routes

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)

app.add_middleware(RequestLoggingMiddleware)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

from slowapi.errors import RateLimitExceeded
from app.core.rate_limit import limiter, custom_rate_limit_exceeded_handler

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "x-request-id"],
)

# Register routers
app.include_router(project_routes.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(user_routes.router, prefix="/api/v1/users", tags=["users"])
app.include_router(idea_routes.router, prefix="/api/v1", tags=["ideas"])
app.include_router(evaluation_routes.router, prefix="/api/v1", tags=["evaluations"])
app.include_router(roadmap_routes.router, prefix="/api/v1", tags=["roadmaps"])
app.include_router(ai_routes.router, prefix="/api/v1", tags=["ai"])
app.include_router(analytics_routes.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/")
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "IdeaGPT API"
    }

@app.get("/health/live", summary="Liveness endpoint")
async def health_live():
    """Fast process liveness check (no DB or vendor dependencies)."""
    return {"status": "live", "service": "IdeaGPT API"}

@app.get("/health/ready", summary="Readiness endpoint")
async def health_ready(response: Response, db: AsyncSession = Depends(get_db)):
    """Database connectivity readiness check."""
    try:
        res = await db.execute(text("SELECT 1"))
        _ = res.scalar()
        return {"status": "ready", "database": "connected"}
    except Exception as exc:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unready", "error": f"Database error: {str(exc)}"}

@app.get("/health/config")
async def health_config():
    """Security configuration state."""
    return settings.get_config_status()

@app.get("/health/ai")
async def health_ai():
    return {
        "status": "healthy",
        "default_provider": settings.DEFAULT_PROVIDER,
        "enabled_providers": {
            "openai": settings.ENABLE_OPENAI,
            "gemini": settings.ENABLE_GEMINI,
            "ollama": settings.ENABLE_OLLAMA,
            "custom": settings.CUSTOM_PROVIDER_URL is not None
        }
    }

@app.get("/health/providers")
async def health_providers():
    import httpx
    status_dict = {}
    
    if not settings.OPENAI_API_KEY:
        status_dict["openai"] = "missing_key"
    else:
        status_dict["openai"] = "available" if settings.ENABLE_OPENAI else "disabled"
        
    if not settings.GEMINI_API_KEY:
        status_dict["gemini"] = "missing_key"
    else:
        status_dict["gemini"] = "available" if settings.ENABLE_GEMINI else "disabled"

    if settings.ENABLE_OLLAMA:
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                res = await client.get(f"{settings.OLLAMA_URL.rstrip('/')}/")
                status_dict["ollama"] = "healthy"
        except Exception:
            status_dict["ollama"] = "offline"
    else:
        status_dict["ollama"] = "disabled"

    if settings.CUSTOM_PROVIDER_URL:
        status_dict["custom"] = "configured"
    else:
        status_dict["custom"] = "not_configured"

    status_dict["mock"] = "healthy"
    return status_dict

@app.get("/metrics", summary="Operational Metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """Exposes operational task metrics and system status."""
    task_count = 0
    status_breakdown = {}
    try:
        res = await db.execute(select(func.count(AiTask.id)))
        task_count = res.scalar() or 0

        breakdown_res = await db.execute(
            select(AiTask.status, func.count(AiTask.id)).group_by(AiTask.status)
        )
        for st, cnt in breakdown_res.all():
            status_breakdown[st] = cnt
    except Exception:
        pass

    return {
        "service": "IdeaGPT API",
        "version": settings.VERSION,
        "app_env": settings.APP_ENV,
        "ai_task_metrics": {
            "total_tasks": task_count,
            "by_status": status_breakdown
        }
    }
