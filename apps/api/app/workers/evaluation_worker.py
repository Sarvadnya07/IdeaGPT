import asyncio
import logging
from app.workers.celery_app import celery_app
from app.evaluation.executor import EvaluationExecutor

logger = logging.getLogger(__name__)

async def _run_pipeline_async(evaluation_id: str):
    logger.info(f"Celery worker running evaluation pipeline for {evaluation_id}...")
    try:
        await EvaluationExecutor.execute_evaluation(evaluation_id)
        logger.info(f"Celery worker finished evaluation pipeline for {evaluation_id}.")
    except Exception as e:
        logger.error(f"Celery worker execution failed for {evaluation_id}: {str(e)}")

@celery_app.task(name="run_evaluation_task")
def run_evaluation_task(evaluation_id: str):
    asyncio.run(_run_pipeline_async(evaluation_id))
