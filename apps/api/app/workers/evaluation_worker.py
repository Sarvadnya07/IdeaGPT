import asyncio
import traceback
import logging
import time
from datetime import datetime
from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.evaluation import Evaluation
from app.models.idea import Idea
from app.services.evaluation_service import evaluation_service

logger = logging.getLogger(__name__)

async def _run_pipeline_async(evaluation_id: str):
    async with AsyncSessionLocal() as db:
        evaluation = await db.get(Evaluation, evaluation_id)
        if not evaluation:
            logger.error(f"Evaluation record {evaluation_id} not found.")
            return

        idea = await db.get(Idea, evaluation.idea_id)
        if not idea:
            logger.error(f"Idea record {evaluation.idea_id} not found.")
            evaluation.status = "FAILED"
            evaluation.progress = "FAILED"
            evaluation.error_message = "Idea record not found."
            await db.commit()
            return

        start_time = time.time()
        try:
            # 1. Initializing state
            evaluation.status = "RUNNING"
            evaluation.progress = "INITIALIZING"
            evaluation.started_at = datetime.utcnow()
            await db.commit()

            # 2. Generating state
            evaluation.progress = "GENERATING"
            await db.commit()

            # Resolve prompt_version if saved in payload previously, default to "1.0"
            payload_meta = evaluation.result_payload.get("metadata", {}) if evaluation.result_payload else {}
            p_ver = payload_meta.get("prompt_version", "1.0")

            # Use routing strategy
            from app.ai.orchestrator.orchestrator import orchestrator
            result_json = await orchestrator.analyze_startup_idea(
                db=db, 
                idea_id=evaluation.idea_id,
                prompt_version=p_ver
            )

            # 3. Parsing state
            evaluation.progress = "PARSING"
            await db.commit()

            # 4. Saving state
            evaluation.progress = "SAVING"
            await db.commit()

            # Record metrics
            duration = int((time.time() - start_time) * 1000)
            evaluation.duration_ms = duration
            evaluation.result_payload = result_json
            evaluation.status = "COMPLETED"
            evaluation.progress = "COMPLETED"
            evaluation.completed_at = datetime.utcnow()
            evaluation.token_usage = 1500  # Simulated token count
            evaluation.estimated_cost = 0.003  # Simulated cost in USD
            
            db.add(evaluation)
            await db.commit()
            logger.info(f"Evaluation {evaluation_id} completed successfully.")

        except Exception as e:
            logger.error(f"Evaluation failed for {evaluation_id}: {str(e)}")
            logger.error(traceback.format_exc())
            evaluation.status = "FAILED"
            evaluation.progress = "FAILED"
            evaluation.error_message = str(e)
            evaluation.completed_at = datetime.utcnow()
            await db.commit()

@celery_app.task(name="run_evaluation_task")
def run_evaluation_task(evaluation_id: str):
    asyncio.run(_run_pipeline_async(evaluation_id))
