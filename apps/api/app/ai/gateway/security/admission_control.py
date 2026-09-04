"""
IdeaGPT AI Gateway — Token-Aware Admission Controller.
Estimates prompt + output tokens, checks budgets, creates reservation tickets,
and reconciles actual consumption after execution.
Supports shared Redis distributed state with bounded local in-memory fallback.
"""

import os
import uuid
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.ai.gateway.security.cost_guardrails import CostGuardrails, CostLimitException

logger = logging.getLogger(__name__)


class AdmissionTicket(BaseModel):
    ticket_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int
    model_id: str
    estimated_input_tokens: int
    estimated_output_tokens: int
    reserved_cost_usd: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "RESERVED"  # RESERVED | RECONCILED | RELEASED


class AdmissionController:
    """
    Admission controller with dual storage:
    - Shared Redis key store if REDIS_URL configured
    - Bounded in-memory fallback with TTL eviction
    """
    _reservations: Dict[str, AdmissionTicket] = {}
    TICKET_TTL_SECONDS: float = 600.0  # 10 minutes max reservation life
    MAX_RESERVATIONS: int = 10000

    @classmethod
    def cleanup_stale_tickets(cls) -> int:
        """Evicts expired reservation tickets to prevent memory leakage."""
        now = datetime.now(timezone.utc)
        stale_keys = [
            tid for tid, ticket in cls._reservations.items()
            if (now - ticket.created_at).total_seconds() > cls.TICKET_TTL_SECONDS
        ]
        for tid in stale_keys:
            cls._reservations.pop(tid, None)
        return len(stale_keys)

    @classmethod
    def estimate_tokens_from_text(cls, text: str) -> int:
        """Heuristic calculation: approx 4 characters per token."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    @classmethod
    def admit_request(
        cls,
        user_id: int,
        prompt: str,
        model_id: str,
        max_output_tokens: int = 2048,
        user_current_daily_spend: float = 0.0
    ) -> AdmissionTicket:
        """
        Performs pre-flight token & cost admission check and creates a reservation ticket.
        """
        # Periodic cleanup of stale tickets
        if len(cls._reservations) > 100:
            cls.cleanup_stale_tickets()

        # Evict oldest if capacity exceeded
        if len(cls._reservations) >= cls.MAX_RESERVATIONS:
            oldest_tid = next(iter(cls._reservations))
            cls._reservations.pop(oldest_tid, None)

        in_tokens = cls.estimate_tokens_from_text(prompt)
        out_tokens = max(100, max_output_tokens)

        cost = CostGuardrails.estimate_cost(model_id, in_tokens, out_tokens)

        # Check guardrail limits
        CostGuardrails.validate_request_cost(cost, user_daily_spend_usd=user_current_daily_spend)

        ticket = AdmissionTicket(
            user_id=user_id,
            model_id=model_id,
            estimated_input_tokens=in_tokens,
            estimated_output_tokens=out_tokens,
            reserved_cost_usd=cost
        )

        # Try saving to Redis if configured
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            try:
                import redis
                r = redis.from_url(redis_url, socket_timeout=1)
                r.set(
                    f"admit:{ticket.ticket_id}",
                    ticket.model_dump_json(),
                    ex=int(cls.TICKET_TTL_SECONDS)
                )
            except Exception as e:
                logger.debug(f"Redis admission save failed: {e}. Stored in local fallback.")

        cls._reservations[ticket.ticket_id] = ticket
        return ticket

    @classmethod
    def reconcile_ticket(
        cls,
        ticket_id: str,
        actual_input_tokens: int,
        actual_output_tokens: int
    ) -> Dict[str, Any]:
        """
        Reconciles actual provider usage against reserved ticket and releases surplus.
        """
        ticket: Optional[AdmissionTicket] = cls._reservations.pop(ticket_id, None)

        # Check Redis if not found in local reservations
        redis_url = os.getenv("REDIS_URL")
        if not ticket and redis_url:
            try:
                import redis
                r = redis.from_url(redis_url, socket_timeout=1)
                val = r.get(f"admit:{ticket_id}")
                if val:
                    ticket_data = json.loads(val.decode("utf-8") if isinstance(val, bytes) else val)
                    ticket = AdmissionTicket(**ticket_data)
                    r.delete(f"admit:{ticket_id}")
            except Exception as e:
                logger.debug(f"Redis admission lookup failed: {e}")

        if not ticket:
            return {"reconciled": False, "reason": "Ticket not found or already reconciled"}

        actual_cost = CostGuardrails.estimate_cost(
            ticket.model_id, actual_input_tokens, actual_output_tokens
        )
        surplus = ticket.reserved_cost_usd - actual_cost

        return {
            "reconciled": True,
            "ticket_id": ticket_id,
            "reserved_cost_usd": ticket.reserved_cost_usd,
            "actual_cost_usd": actual_cost,
            "cost_delta_usd": round(surplus, 6)
        }
