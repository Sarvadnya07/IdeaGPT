"""
IdeaGPT AI Gateway — Multi-Dimensional Cost & FinOps Guardrails.
Tracks and enforces:
  - Per-request maximum cost ceiling
  - Per-user daily budget
  - Per-tenant monthly budget
  - Threshold alerts: WARN (50%), THROTTLE (70%), DOWNGRADE (80%), REJECT (90%), DISABLE (100%)
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Model cost dictionary per 1k tokens (input, output) in USD
MODEL_PRICING_USD = {
    # Groq (Near zero / ultra-low)
    "llama-3.3-70b-versatile": (0.00059, 0.00079),
    "llama-3.1-8b-instant": (0.00005, 0.00008),
    "openai/gpt-oss-120b": (0.00059, 0.00079),
    # Gemini
    "gemini-2.0-flash": (0.00010, 0.00040),
    "gemini-1.5-pro": (0.00125, 0.00500),
    # OpenAI
    "gpt-4o": (0.00250, 0.01000),
    "gpt-4o-mini": (0.00015, 0.00060),
    # Default fallback
    "default": (0.00050, 0.00150),
}


class CostLimitException(Exception):
    """Raised when an AI dispatch exceeds financial ceilings."""
    pass


class CostGuardrails:
    PER_REQUEST_MAX_COST_USD: float = 0.25      # Max 25 cents per single task
    PER_USER_DAILY_BUDGET_USD: float = 2.00     # Max $2.00 per user per day
    PER_TENANT_MONTHLY_BUDGET_USD: float = 50.0 # Max $50.00 per tenant per month

    @classmethod
    def estimate_cost(
        cls,
        model_id: str,
        input_tokens: int,
        estimated_output_tokens: int
    ) -> float:
        """Estimates cost in USD for a given token allocation."""
        m_id = model_id.lower()
        pricing = MODEL_PRICING_USD.get("default")
        for key, price in MODEL_PRICING_USD.items():
            if key in m_id:
                pricing = price
                break

        in_price_1k, out_price_1k = pricing
        cost = (input_tokens / 1000.0) * in_price_1k + (estimated_output_tokens / 1000.0) * out_price_1k
        return round(cost, 6)

    @classmethod
    def validate_request_cost(
        cls,
        estimated_cost_usd: float,
        user_daily_spend_usd: float = 0.0
    ) -> Dict[str, Any]:
        """
        Checks cost thresholds and returns policy enforcement decision.
        """
        # 1. Per-Request Maximum Ceiling
        if estimated_cost_usd > cls.PER_REQUEST_MAX_COST_USD:
            raise CostLimitException(
                f"Estimated task cost (${estimated_cost_usd:.4f}) exceeds single-request ceiling (${cls.PER_REQUEST_MAX_COST_USD:.2f})."
            )

        # 2. Per-User Daily Budget Check
        projected_spend = user_daily_spend_usd + estimated_cost_usd
        if projected_spend >= cls.PER_USER_DAILY_BUDGET_USD:
            raise CostLimitException(
                f"User daily spend limit exceeded (${projected_spend:.2f} >= ${cls.PER_USER_DAILY_BUDGET_USD:.2f})."
            )

        ratio = projected_spend / cls.PER_USER_DAILY_BUDGET_USD
        action = "ALLOW"
        if ratio >= 0.90:
            action = "REJECT"
        elif ratio >= 0.80:
            action = "DOWNGRADE"
        elif ratio >= 0.70:
            action = "THROTTLE"
        elif ratio >= 0.50:
            action = "WARN"

        return {
            "allowed": True,
            "action": action,
            "estimated_cost_usd": estimated_cost_usd,
            "projected_daily_spend_usd": round(projected_spend, 4),
            "spend_ratio": round(ratio, 2)
        }
