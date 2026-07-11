import asyncio
import traceback
import logging
from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.evaluation import EvaluationJob, Evaluation
from app.models.idea import Idea
from app.services.ai.orchestrator import orchestrator

logger = logging.getLogger(__name__)

async def _run_pipeline_async(job_id: int, idea_id: int):
    async with AsyncSessionLocal() as db:
        job = await db.get(EvaluationJob, job_id)
        idea = await db.get(Idea, idea_id)
        
        if not job or not idea:
            return
            
        try:
            job.status = "processing"
            await db.commit()

            # Abstracted prompt builder
            prompt = f"""
            Analyze the following startup idea submission.
            
            Problem: {idea.problem_statement}
            Solution: {idea.solution_description}
            Target Audience: {idea.target_audience}
            Business Model: {idea.business_model}
            Competitors: {idea.competitors}
            USP: {idea.unique_selling_proposition}
            Tech Stack: {idea.technology_stack}
            Budget: {idea.budget}
            Timeline: {idea.timeline}
            Additional Notes: {idea.additional_notes}
            
            Provide a structured JSON output with the following keys:
            - "score": A number out of 100 representing overall potential.
            - "strengths": Array of strings.
            - "weaknesses": Array of strings.
            - "market_analysis": A short paragraph.
            - "recommendations": Array of strings.
            """
            
            result_json = await orchestrator.analyze_startup_idea(prompt=prompt, provider_name="openai")
            
            evaluation = Evaluation(job_id=job.id, result_data=result_json)
            db.add(evaluation)
            
            job.status = "completed"
            await db.commit()
            
        except Exception as e:
            logger.error(f"Evaluation failed for job {job_id}: {str(e)}")
            logger.error(traceback.format_exc())
            job.status = "failed"
            job.error_message = str(e)
            await db.commit()

@celery_app.task(name="run_evaluation_task")
def run_evaluation_task(job_id: int, idea_id: int):
    # Celery runs in a synchronous worker, so we use asyncio.run to execute the async pipeline
    asyncio.run(_run_pipeline_async(job_id, idea_id))
