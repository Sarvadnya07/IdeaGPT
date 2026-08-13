import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.ai_task import AiTask
from app.models.user import User
from app.ai.exceptions.ai_exceptions import AIQuotaExceededException, AIInvalidInputException

logger = logging.getLogger(__name__)

class AIQuotaService:
    MAX_PROMPT_CHARS: int = 8000
    DAILY_TASK_QUOTA_PER_USER: int = 20

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
