import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

STATUS_TITLES = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    409: "Conflict",
    422: "Unprocessable Entity",
    429: "Too Many Requests",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout"
}


def _get_request_id(request: Request) -> str:
    """Safely read the correlation ID set by RequestLoggingMiddleware."""
    return getattr(request.state, "request_id", "") or ""


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    title = STATUS_TITLES.get(exc.status_code, "HTTP Error")
    request_id = _get_request_id(request)
    headers = dict(getattr(exc, "headers", None) or {})
    headers["x-request-id"] = request_id

    return JSONResponse(
        status_code=exc.status_code,
        headers=headers,
        content={
            "type": f"https://httpstatuses.com/{exc.status_code}",
            "title": title,
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": request.url.path,
            "request_id": request_id,
            # Backward-compatible fields
            "error": exc.detail,
            "code": str(exc.status_code),
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_msg = "Validation Error"
    if errors:
        error_msg = f"{errors[0]['loc'][-1]}: {errors[0]['msg']}"

    invalid_params = []
    for err in errors:
        loc_path = ".".join(str(l) for l in err.get("loc", []) if l != "body")
        invalid_params.append({
            "name": loc_path or "body",
            "reason": err.get("msg", ""),
            "type": err.get("type", "")
        })

    request_id = _get_request_id(request)

    return JSONResponse(
        status_code=422,
        headers={"x-request-id": request_id},
        content={
            "type": "https://httpstatuses.com/422",
            "title": "Unprocessable Entity",
            "status": 422,
            "detail": error_msg,
            "instance": request.url.path,
            "request_id": request_id,
            # Backward-compatible fields
            "error": error_msg,
            "code": "422_VALIDATION_ERROR",
            "details": errors,
            "invalid_params": invalid_params,
        }
    )

async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception during %s %s", request.method, request.url.path, exc_info=exc)
    request_id = _get_request_id(request)
    return JSONResponse(
        status_code=500,
        headers={"x-request-id": request_id},
        content={
            "type": "https://httpstatuses.com/500",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred processing your request.",
            "instance": request.url.path,
            "request_id": request_id,
            # Backward-compatible fields
            "error": "Internal Server Error",
            "code": "500_INTERNAL_ERROR"
        }
    )
