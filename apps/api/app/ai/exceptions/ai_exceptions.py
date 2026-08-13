class AIException(Exception):
    """Base exception for AI platform errors."""
    def __init__(self, message: str, status_code: int = 500, code: str = "AI_ERROR", is_retryable: bool = False):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.is_retryable = is_retryable

class AIUnavailableException(AIException):
    def __init__(self, message: str = "No AI provider is currently configured or available."):
        super().__init__(message=message, status_code=503, code="AI_UNAVAILABLE", is_retryable=True)

class AIInvalidModelException(AIException):
    def __init__(self, message: str = "The selected provider or model is invalid or unavailable."):
        super().__init__(message=message, status_code=400, code="INVALID_MODEL", is_retryable=False)

class AIAuthenticationException(AIException):
    def __init__(self, message: str = "Provider authentication failed (invalid API key)."):
        super().__init__(message=message, status_code=401, code="AUTHENTICATION_ERROR", is_retryable=False)

class AIRateLimitException(AIException):
    def __init__(self, message: str = "AI provider rate limit exceeded."):
        super().__init__(message=message, status_code=429, code="RATE_LIMITED", is_retryable=True)

class AITimeoutException(AIException):
    def __init__(self, message: str = "AI provider request timed out."):
        super().__init__(message=message, status_code=504, code="TIMEOUT", is_retryable=True)

class AINetworkException(AIException):
    def __init__(self, message: str = "Transient network error while reaching AI provider."):
        super().__init__(message=message, status_code=502, code="NETWORK_ERROR", is_retryable=True)

class AIQuotaExceededException(AIException):
    def __init__(self, message: str = "User daily AI token/evaluation quota exceeded."):
        super().__init__(message=message, status_code=429, code="QUOTA_EXCEEDED", is_retryable=False)

class AIInvalidInputException(AIException):
    def __init__(self, message: str = "Input prompt exceeds maximum allowed length."):
        super().__init__(message=message, status_code=400, code="INVALID_REQUEST", is_retryable=False)
