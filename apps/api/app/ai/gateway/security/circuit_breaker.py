"""
IdeaGPT AI Gateway — Per-Provider Circuit Breaker.
States: CLOSED (Normal) -> OPEN (Failing) -> HALF_OPEN (Probing)
Prevents cascading failure storms when external AI providers experience outages.
"""

import time
import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class ProviderCircuitBreaker:
    def __init__(
        self,
        provider_id: str,
        failure_threshold: int = 5,
        cooldown_seconds: float = 30.0
    ):
        self.provider_id = provider_id
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.last_failure_time: float = 0.0

    def can_execute(self) -> bool:
        """Determines if a request can be dispatched to this provider."""
        now = time.time()
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if (now - self.last_failure_time) >= self.cooldown_seconds:
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit for provider '{self.provider_id}' transitioned to HALF_OPEN (probing).")
                return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            return True
        return False

    def record_success(self) -> None:
        """Records successful response and resets circuit to CLOSED."""
        self.consecutive_failures = 0
        if self.state != CircuitState.CLOSED:
            logger.info(f"Circuit for provider '{self.provider_id}' recovered -> CLOSED.")
        self.state = CircuitState.CLOSED

    def record_failure(self, is_fatal: bool = True) -> None:
        """
        Records failure and transitions to OPEN if failure threshold is reached.
        Auth errors and invalid user inputs do NOT trip the circuit.
        """
        if not is_fatal:
            return

        self.consecutive_failures += 1
        self.last_failure_time = time.time()

        if self.consecutive_failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit for provider '{self.provider_id}' TRIPPED to OPEN ({self.consecutive_failures} failures)."
            )


class CircuitBreakerRegistry:
    _breakers: Dict[str, ProviderCircuitBreaker] = {}

    @classmethod
    def get_breaker(cls, provider_id: str) -> ProviderCircuitBreaker:
        p_id = provider_id.lower()
        if p_id not in cls._breakers:
            cls._breakers[p_id] = ProviderCircuitBreaker(p_id)
        return cls._breakers[p_id]
