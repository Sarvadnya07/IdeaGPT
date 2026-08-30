from fastapi import FastAPI, Depends, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
from typing import Annotated

from app.core.config import settings
from app.core.logging import RequestLoggingMiddleware
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
from app.db.session import get_db
from app.models.ai_task import AiTask
from app.models.user import User
from app.api.dependencies.auth import get_current_user
from app.api.routes import (
    project_routes,
    user_routes,
    idea_routes,
    evaluation_routes,
    roadmap_routes,
    ai_routes,
    analytics_routes,
    credential_routes,
)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    import os
    import logging
    logger = logging.getLogger("uvicorn.error")

    # Startup: Safely validate production configuration and log diagnostics
    try:
        settings.validate_production_config()
    except RuntimeError as err:
        logger.error("PRODUCTION CONFIGURATION WARNING: %s", err)

    # Pre-warm database connection pool on non-serverless dedicated instances
    is_serverless = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
    if not is_serverless:
        try:
            from app.core.database import engine
            from app.db.session import AsyncSessionLocal
            from app.evaluation.coordinator import EvaluationCoordinator
            from app.services.ai_task_service import AiTaskService
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            async with AsyncSessionLocal() as db:
                await EvaluationCoordinator.recover_stale_evaluations(db, threshold_seconds=300)
                await AiTaskService.cleanup_stale_tasks(db, timeout_minutes=5)
        except Exception as exc:
            logger.warning("Dedicated server pre-warm warning: %s", exc)
    yield
    # Shutdown: Dispose engine gracefully
    try:
        from app.core.database import engine
        await engine.dispose()
    except Exception:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
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
app.include_router(credential_routes.router, prefix="/api/v1", tags=["credentials"])
app.include_router(analytics_routes.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/")
@app.get("/api")
@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "IdeaGPT API"
    }

@app.get("/health/live", summary="Liveness endpoint")
@app.get("/api/health/live", summary="Liveness endpoint (prefixed)")
async def health_live():
    """Fast process liveness check (no DB or vendor dependencies)."""
    return {"status": "live", "service": "IdeaGPT API"}

@app.get("/health/ready", summary="Readiness endpoint")
@app.get("/api/health/ready", summary="Readiness endpoint (prefixed)")
async def health_ready(response: Response, db: AsyncSession = Depends(get_db)):
    """Database connectivity readiness check."""
    try:
        res = await db.execute(text("SELECT 1"))
        _ = res.scalar()
        return {"status": "ready", "database": "connected"}
    except Exception as exc:
        import logging
        logging.getLogger("ideagpt.health").error(f"Readiness check failed: {exc}", exc_info=True)
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unready", "error": "Database connectivity check failed"}

# ---------------------------------------------------------------------------
# Authenticated operational endpoints
# These endpoints expose configuration/operational details and require auth.
# ---------------------------------------------------------------------------

@app.get("/health/config")
@app.get("/api/health/config")
async def health_config(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Security configuration state (authenticated)."""
    return settings.get_config_status()

@app.get("/health/ai")
@app.get("/api/health/ai")
async def health_ai(
    current_user: Annotated[User, Depends(get_current_user)]
):
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
@app.get("/api/health/providers")
async def health_providers(
    current_user: Annotated[User, Depends(get_current_user)]
):
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
@app.get("/api/metrics", summary="Operational Metrics (prefixed)")
async def get_metrics(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Exposes operational task metrics and system status (authenticated)."""
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
        "ai_task_metrics": {
            "total_tasks": task_count,
            "by_status": status_breakdown
        }
    }
