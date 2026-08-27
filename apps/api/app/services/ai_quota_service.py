import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.ai_task import AiTask
from app.models.user import User
from app.ai.exceptions.ai_exceptions import (
    AIQuotaExceededException,
    AIInvalidInputException,
    AIRateLimitException,
)
from app.ai.gateway.security.admission_control import AdmissionController, AdmissionTicket
from app.ai.gateway.security.cost_guardrails import CostGuardrails, CostLimitException

logger = logging.getLogger(__name__)

class AIQuotaService:
    MAX_PROMPT_CHARS: int = 8000
    DAILY_TASK_QUOTA_PER_USER: int = 20
    MAX_CONCURRENT_TASKS_PER_USER: int = 3

    @classmethod
    def validate_input_length(cls, prompt: str):
        """
        Enforces server-side max input length validation.
        """
        if not prompt or len(prompt.strip()) == 0:
            raise AIInvalidInputException("Prompt cannot be empty.")
        if len(prompt) > cls.MAX_PROMPT_CHARS:
            raise AIInvalidInputException(
                f"Prompt exceeds maximum character length limit ({len(prompt)} > {cls.MAX_PROMPT_CHARS})."
            )

    @classmethod
    async def check_user_quota(cls, db: AsyncSession, user: User):
        """
        Enforces per-user daily AI task evaluation quota.
        """
        now = datetime.now(timezone.utc)
        start_of_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

        stmt = select(func.count(AiTask.id)).where(
            and_(
                AiTask.user_id == user.id,
                AiTask.created_at >= start_of_day,
                AiTask.status.in_(["QUEUED", "RUNNING", "COMPLETED"])
            )
        )
        res = await db.execute(stmt)
        count = res.scalar() or 0

        if count >= cls.DAILY_TASK_QUOTA_PER_USER:
            logger.warning(f"User {user.id} ({user.clerk_id}) exceeded daily AI task quota ({count}/{cls.DAILY_TASK_QUOTA_PER_USER})")
            raise AIQuotaExceededException(
                f"Daily AI task quota limit reached ({count}/{cls.DAILY_TASK_QUOTA_PER_USER}). Please try again tomorrow."
            )

    @classmethod
    async def check_user_concurrency(cls, db: AsyncSession, user: User):
        """
        Enforces maximum concurrent running AI tasks per user to prevent worker starvation.
        """
        stmt = select(func.count(AiTask.id)).where(
            and_(
                AiTask.user_id == user.id,
                AiTask.status == "RUNNING"
            )
        )
        res = await db.execute(stmt)
        running_count = res.scalar() or 0

        if running_count >= cls.MAX_CONCURRENT_TASKS_PER_USER:
            logger.warning(f"User {user.id} exceeded concurrent AI task limit ({running_count}/{cls.MAX_CONCURRENT_TASKS_PER_USER})")
            raise AIRateLimitException(
                f"Concurrent task execution limit reached ({running_count}/{cls.MAX_CONCURRENT_TASKS_PER_USER}). Please wait for in-flight tasks to complete."
            )

    @classmethod
    def check_token_admission(
        cls,
        user_id: int,
        prompt: str,
        model_id: str,
        max_output_tokens: int = 2048,
        user_current_daily_spend: float = 0.0
    ) -> AdmissionTicket:
        """
        Pre-flight cost and token reservation check.
        """
        try:
            return AdmissionController.admit_request(
                user_id=user_id,
                prompt=prompt,
                model_id=model_id,
                max_output_tokens=max_output_tokens,
                user_current_daily_spend=user_current_daily_spend
            )
        except CostLimitException as cle:
            raise AIQuotaExceededException(str(cle))
