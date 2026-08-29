import uuid
import logging
import json
import time
from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class JSONLogFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logging():
    logger = logging.getLogger("ideagpt")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JSONLogFormatter())
    logger.addHandler(handler)
    return logger

logger = setup_logging()

import re

_SAFE_REQUEST_ID_REGEX = re.compile(r"^[a-zA-Z0-9_\-]{1,64}$")

def sanitize_request_id(raw_id: str | None) -> str:
    """
    Validate and sanitize client-provided correlation ID.
    - If valid safe alphanumeric/UUID string (1-64 chars, only a-z, A-Z, 0-9, _, -): accept.
    - Otherwise (garbage with spaces, newlines, control characters, script injection, oversized): generate server-side UUIDv4.
    """
    if not raw_id:
        return str(uuid.uuid4())

    cleaned = raw_id.strip()
    if _SAFE_REQUEST_ID_REGEX.match(cleaned):
        return cleaned

    return str(uuid.uuid4())

def _sanitize_url(url: str) -> str:
    """Redact sensitive query parameters from logged URLs."""
    import re
    sensitive_keys = r"(token|key|secret|password|code|credential|api_key|access_token|refresh_token)"
    pattern = re.compile(rf"([?&]{sensitive_keys}=)([^&]+)", re.IGNORECASE)
    return pattern.sub(r"\1[REDACTED]", url)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Validated and sanitized correlation ID
        raw_header = request.headers.get("x-request-id")
        request_id = sanitize_request_id(raw_header)
        request.state.request_id = request_id

        response = await call_next(request)
        process_time = time.time() - start_time
        
        response.headers["x-request-id"] = request_id

        # Mask client IP if multiple proxy headers exist or sanitize
        client_ip = request.client.host if request.client else None

        log_dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "INFO",
            "request_id": request_id,
            "method": request.method,
            "url": _sanitize_url(str(request.url)),
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time_ms": round(process_time * 1000, 2),
            "client_ip": client_ip
        }
        
        print(json.dumps(log_dict))
        return response

