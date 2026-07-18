from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.core.logging import RequestLoggingMiddleware
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)

from app.api.routes import project_routes, user_routes, idea_routes, evaluation_routes

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)

app.add_middleware(RequestLoggingMiddleware)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS (Restricted)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://ideagpt.dev" # Production example
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Register routers
app.include_router(project_routes.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(user_routes.router, prefix="/api/v1/users", tags=["users"])
app.include_router(idea_routes.router, prefix="/api/v1/projects", tags=["ideas"])
app.include_router(evaluation_routes.router, prefix="/api/v1", tags=["evaluations"])

@app.get("/")
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "IdeaGPT API"
    }

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
    status = {}
    
    if not settings.OPENAI_API_KEY:
        status["openai"] = "missing_key"
    else:
        status["openai"] = "available" if settings.ENABLE_OPENAI else "disabled"
        
    if not settings.GEMINI_API_KEY:
        status["gemini"] = "missing_key"
    else:
        status["gemini"] = "available" if settings.ENABLE_GEMINI else "disabled"

    if settings.ENABLE_OLLAMA:
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                res = await client.get(f"{settings.OLLAMA_URL.rstrip('/')}/")
                status["ollama"] = "healthy"
        except Exception:
            status["ollama"] = "offline"
    else:
        status["ollama"] = "disabled"

    if settings.CUSTOM_PROVIDER_URL:
        status["custom"] = "configured"
    else:
        status["custom"] = "not_configured"

    status["mock"] = "healthy"
    return status
