from fastapi import FastAPI, Depends, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
from typing import Annotated
import asyncio

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
        if settings.APP_ENV == "production":
            # F-04: fail closed — a known-insecure production configuration must not boot.
            logger.critical("PRODUCTION CONFIGURATION FAILURE: %s", err)
            raise
        logger.error("PRODUCTION CONFIGURATION WARNING: %s", err)

    # Pre-warm database connection pool on non-serverless dedicated instances
    is_serverless = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
    if not is_serverless:
        try:
            async def _prewarm():
                from app.core.database import engine
                from app.db.session import AsyncSessionLocal
                from app.evaluation.coordinator import EvaluationCoordinator
                from app.services.ai_task_service import AiTaskService
                async with engine.begin() as conn:
                    await conn.execute(text("SELECT 1"))
                async with AsyncSessionLocal() as db:
                    await EvaluationCoordinator.recover_stale_evaluations(db, threshold_seconds=300)
                    await AiTaskService.cleanup_stale_tasks(db, timeout_minutes=5)

            await asyncio.wait_for(_prewarm(), timeout=3.0)
        except Exception as exc:
            logger.warning("Dedicated server pre-warm warning: %s", exc)
    yield
    # Shutdown: Dispose engine and redis pool gracefully
    try:
        from app.core.database import engine
        await engine.dispose()
    except Exception:
        pass
    try:
        from app.core.redis import close_redis_pool
        await close_redis_pool()
    except Exception:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

from app.core.metrics import (
    PrometheusMetricsMiddleware,
    get_prometheus_exposition_text,
    update_ai_tasks_gauge,
)

app.add_middleware(PrometheusMetricsMiddleware)
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
    allow_methods=["*"],
    allow_headers=["*"],
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
async def health_ready(response: Response):
    """Database connectivity readiness check."""
    try:
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            res = await db.execute(text("SELECT 1"))
            _ = res.scalar()
            return {"status": "ready", "database": "connected"}
    except Exception as exc:
        import logging
        exc_type = type(exc).__name__
        logging.getLogger("ideagpt.health").error(f"Readiness check failed: {exc_type}: {exc}", exc_info=True)
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unready", "error": "Database connectivity check failed", "failure_type": exc_type}

# ---------------------------------------------------------------------------
# Authenticated operational endpoints
# These endpoints expose configuration/operational details and require auth.
# ---------------------------------------------------------------------------

from app.api.dependencies.auth import verify_metrics_auth

@app.get("/health/config")
@app.get("/api/health/config")
async def health_config(
    _: Annotated[bool, Depends(verify_metrics_auth)]
):
    """Security configuration state (authenticated)."""
    return settings.get_config_status()

@app.get("/health/ai")
@app.get("/api/health/ai")
async def health_ai(
    _: Annotated[bool, Depends(verify_metrics_auth)]
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
    _: Annotated[bool, Depends(verify_metrics_auth)]
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


@app.get("/health/db-diagnostics", summary="Database Runtime Diagnostics (authenticated)")
@app.get("/api/health/db-diagnostics", summary="Database Runtime Diagnostics (prefixed)")
async def health_db_diagnostics(_: Annotated[bool, Depends(verify_metrics_auth)]):
    """
    Executes in-container database diagnostics:
    - Environment variables presence
    - Connection target URL (sanitized with credentials redacted)
    - DNS resolution
    - TCP reachability
    - TLS/SSL handshake & Auth
    - SELECT 1 & SELECT version()
    - Table inventory
    - Failure classification
    """
    import os
    import socket
    import asyncio
    from sqlalchemy.engine import make_url

    raw_url = os.getenv("DATABASE_URL") or settings.DATABASE_URL or ""
    redis_url = os.getenv("REDIS_URL")

    safe_db_url = "MISSING"
    host = None
    port = 5432
    driver = "unknown"
    if raw_url:
        try:
            u = make_url(raw_url)
            driver = u.drivername
            host = u.host
            port = u.port or 5432
            safe_db_url = u.render_as_string(hide_password=True)
        except Exception as e:
            safe_db_url = f"MALFORMED: {type(e).__name__}"

    env_status = {
        "DATABASE_URL": "PRESENT" if os.getenv("DATABASE_URL") else "MISSING",
        "POSTGRES_DATABASE_URL": "PRESENT" if os.getenv("POSTGRES_DATABASE_URL") else "MISSING",
        "DATABASE_PUBLIC_URL": "PRESENT" if os.getenv("DATABASE_PUBLIC_URL") else "MISSING",
        "DATABASE_PRIVATE_URL": "PRESENT" if os.getenv("DATABASE_PRIVATE_URL") else "MISSING",
        "PGHOST": "PRESENT" if os.getenv("PGHOST") else "MISSING",
        "PGPORT": "PRESENT" if os.getenv("PGPORT") else "MISSING",
        "PGUSER": "PRESENT" if os.getenv("PGUSER") else "MISSING",
        "PGDATABASE": "PRESENT" if os.getenv("PGDATABASE") else "MISSING",
        "REDIS_URL": "PRESENT" if redis_url else "MISSING",
        "APP_ENV": settings.APP_ENV,
    }

    diag = {
        "env": env_status,
        "connection_target": safe_db_url,
        "host": host,
        "port": port,
        "driver": driver,
        "dns": "NOT_TESTED",
        "tcp": "NOT_TESTED",
        "tls_ssl": "NOT_TESTED",
        "auth_query": "NOT_TESTED",
        "select_1": "NOT_TESTED",
        "version": None,
        "current_database": None,
        "tables": [],
        "failure_class": None,
        "error_details": None,
    }

    if not host or "sqlite" in driver:
        diag["dns"] = "SKIPPED_SQLITE"
        diag["tcp"] = "SKIPPED_SQLITE"
        diag["tls_ssl"] = "SKIPPED_SQLITE"
        try:
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                res = await session.execute(text("SELECT 1;"))
                diag["select_1"] = "OK" if res.scalar() == 1 else "FAILED"
                diag["auth_query"] = "OK"
        except Exception as exc:
            diag["failure_class"] = "SQLITE_ERROR"
            diag["error_details"] = f"{type(exc).__name__}: {exc}"
        return diag

    # 1. DNS Resolution
    resolved_ips = []
    try:
        addr_info = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for item in addr_info:
            ip_str = str(item[4][0])
            if ip_str not in resolved_ips:
                resolved_ips.append(ip_str)
        diag["dns"] = f"OK ({', '.join(resolved_ips)})"
    except socket.gaierror as gai:
        diag["dns"] = f"FAILED: {gai}"
        diag["failure_class"] = "A_DNS"
        diag["error_details"] = f"socket.gaierror: {gai}"
        return diag
    except Exception as exc:
        diag["dns"] = f"FAILED: {type(exc).__name__}: {exc}"
        diag["failure_class"] = "A_DNS"
        diag["error_details"] = str(exc)
        return diag

    # 2. TCP Reachability
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=3.0)
        writer.close()
        await writer.wait_closed()
        diag["tcp"] = f"OK (connected to {host}:{port})"
    except asyncio.TimeoutError:
        diag["tcp"] = "FAILED (Timeout after 3s)"
        diag["failure_class"] = "D_TIMEOUT"
        diag["error_details"] = f"TCP connection timed out to {host}:{port}"
        return diag
    except ConnectionRefusedError as cre:
        diag["tcp"] = "FAILED (Connection Refused)"
        diag["failure_class"] = "C_CONNECTION_REFUSED"
        diag["error_details"] = f"Connection refused on {host}:{port}"
        return diag
    except Exception as exc:
        diag["tcp"] = f"FAILED: {type(exc).__name__}: {exc}"
        diag["failure_class"] = "B_NETWORK_ROUTING"
        diag["error_details"] = str(exc)
        return diag

    # 3. PostgreSQL Handshake / Auth / Query
    try:
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            res1 = await session.execute(text("SELECT 1;"))
            _ = res1.scalar()
            diag["select_1"] = "OK"
            diag["auth_query"] = "OK"
            diag["tls_ssl"] = "OK"

            v_res = await session.execute(text("SELECT version();"))
            diag["version"] = v_res.scalar()

            db_res = await session.execute(text("SELECT current_database();"))
            diag["current_database"] = db_res.scalar()

            t_res = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"))
            diag["tables"] = [row[0] for row in t_res.all()]
    except Exception as exc:
        exc_name = type(exc).__name__
        exc_str = str(exc)
        diag["auth_query"] = f"FAILED: {exc_name}"
        diag["error_details"] = f"{exc_name}: {exc_str}"

        # Classify
        if "InvalidPassword" in exc_name or "password authentication failed" in exc_str.lower():
            diag["failure_class"] = "E_AUTHENTICATION"
        elif "InvalidCatalogName" in exc_name or "does not exist" in exc_str.lower():
            diag["failure_class"] = "F_DATABASE_DOES_NOT_EXIST"
        elif "SSLError" in exc_name or "ssl" in exc_str.lower():
            diag["failure_class"] = "G_SSL"
            diag["tls_ssl"] = f"FAILED: {exc_name}"
        elif "Timeout" in exc_name:
            diag["failure_class"] = "D_TIMEOUT"
        elif "ConnectionRefused" in exc_name:
            diag["failure_class"] = "C_CONNECTION_REFUSED"
        else:
            diag["failure_class"] = "I_APPLICATION_CONFIGURATION"

    return diag

@app.get("/metrics", summary="Prometheus Operational Metrics", response_class=Response)
@app.get("/api/metrics", summary="Prometheus Operational Metrics (prefixed)", response_class=Response)
async def get_metrics(
    _: Annotated[bool, Depends(verify_metrics_auth)],
):
    """
    Exposes standard Prometheus text exposition format (version 0.0.4).
    Requires authentication (valid Clerk session JWT or METRICS_SCRAPE_TOKEN).
    """
    try:
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            breakdown_res = await db.execute(
                select(AiTask.status, func.count(AiTask.id)).group_by(AiTask.status)
            )
            status_breakdown = {str(st): int(cnt) for st, cnt in breakdown_res.all()}
            update_ai_tasks_gauge(status_breakdown)
    except Exception as exc:
        import logging
        logging.getLogger("ideagpt.metrics").warning("Database task metrics refresh failed: %s", exc)

    return Response(
        content=get_prometheus_exposition_text(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
