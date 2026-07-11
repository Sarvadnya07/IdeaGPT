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
async def health_check():
    return {
        "status": "healthy",
        "service": "IdeaGPT API"
    }
