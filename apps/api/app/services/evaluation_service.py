import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
import traceback

from app.models.evaluation import EvaluationJob, Evaluation
from app.models.idea import Idea
from app.models.project import Project
from app.db.session import AsyncSessionLocal
from app.ai import orchestrator

logger = logging.getLogger(__name__)

class EvaluationService:
    async def _verify_project_ownership(self, db: AsyncSession, project_id: str, user_id: int):
        result = await db.execute(select(Project).where(Project.id == project_id, Project.user_id == user_id, Project.deleted_at.is_(None)))
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found or access denied")
        return project

    async def get_job_status(self, db: AsyncSession, job_id: int, user_id: int):
        result = await db.execute(
            select(EvaluationJob, Idea)
            .join(Idea, Idea.id == EvaluationJob.idea_id)
            .where(EvaluationJob.id == job_id)
        )
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job, idea = row
        await self._verify_project_ownership(db, idea.project_id, user_id)
        
        return job

    async def trigger_evaluation(self, db: AsyncSession, project_id: str, user_id: int):
        await self._verify_project_ownership(db, project_id, user_id)
        
        # 1. Fetch Latest Idea
        result = await db.execute(select(Idea).where(Idea.project_id == project_id).order_by(Idea.created_at.desc()))
        idea = result.scalars().first()
        if not idea:
            raise HTTPException(status_code=404, detail="Idea submission not found for this project")
            
        # 2. Check if a queued or processing job already exists
        job_res = await db.execute(
            select(EvaluationJob).where(
                EvaluationJob.idea_id == idea.id,
                EvaluationJob.status.in_(["queued", "processing"])
            )
        )
        if job_res.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Evaluation already in progress")

        # 3. Create a Job in 'queued' state
        job = EvaluationJob(idea_id=idea.id, status="queued")
        db.add(job)
        await db.commit()
        await db.refresh(job)

        # 4. Enqueue Celery Task
        from app.workers.evaluation_worker import run_evaluation_task
        run_evaluation_task.delay(job.id, idea.id)
        
        return job

    async def run_evaluation_pipeline(self, job_id: int, idea_id: str):
        """
        Background task to run the AI pipeline via Orchestrator.
        """
        async with AsyncSessionLocal() as db:
            job = await db.get(EvaluationJob, job_id)
            idea = await db.get(Idea, idea_id)
            
            if not job or not idea:
                return
                
            try:
                # Update status to processing
                job.status = "processing"
                await db.commit()

                # Call AI Orchestrator
                prompt = self._build_prompt(idea)
                
                # Provider logic is abstracted entirely.
                result_json = await orchestrator.analyze_startup_idea(prompt=prompt, provider_name="openai")
                
                # Save Evaluation
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

    def _build_prompt(self, idea: Idea) -> str:
        return f'''
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
        '''

evaluation_service = EvaluationService()
