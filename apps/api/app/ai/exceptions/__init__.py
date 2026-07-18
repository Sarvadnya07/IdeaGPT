# Exceptions subpackage
class AIException(Exception):
    """Base exception for all AI platform errors."""
    pass

class MissingApiKeyException(AIException):
    pass

class RateLimitException(AIException):
    pass

class TimeoutException(AIException):
    pass

class InvalidResponseException(AIException):
    pass

class ProviderUnavailableException(AIException):
    pass
