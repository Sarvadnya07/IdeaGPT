from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "code": str(exc.status_code)
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_msg = "Validation Error"
    if errors:
        error_msg = f"{errors[0]['loc'][-1]}: {errors[0]['msg']}"
        
    return JSONResponse(
        status_code=422,
        content={
            "error": error_msg,
            "code": "422_VALIDATION_ERROR",
            "details": errors
        }
    )

import logging

logger = logging.getLogger(__name__)

async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception during %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "code": "500_INTERNAL_ERROR"
        }
    )
