from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.idea import Idea
from app.models.project import Project

class ContextBuilder:
    @staticmethod
    def compile_context(idea: Any, project: Any) -> Dict[str, Any]:
        """
        Pure context assembly from detached Idea / Project entities.

        Split out of build_context() (PRODUCT-01 P-07) so a caller that already
        holds the rows can render the identical prompt WITHOUT keeping a database
        session — and therefore a pooled connection — open across the external
        LLM call. The output of this function is byte-for-byte what build_context()
        has always produced.
        """
        # Compile variables dictionary
        context = {
            "project_id": project.id,
            "project_title": project.title,
            "project_description": project.description or "",
            "project_category": project.category or "",
            "idea_id": idea.id,
            "idea_title": idea.title,
            "problem_statement": idea.problem_statement,
            "solution_description": idea.solution_description,
            "target_users": idea.target_users or "General Public",
            "industry": idea.industry or "Technology",
            "business_model": idea.business_model or "SaaS",
            "stage": idea.stage or "Concept",
            "tags": idea.tags or "",
            "notes": idea.notes or "",
        }

        # Handle backward-compatible naming for dashboard analyses
        context.update({
            "elevator_pitch": idea.problem_statement,
            "core_problem": idea.problem_statement,
            "target_audience": idea.target_users or "General Public",
        })

        return context

    @staticmethod
    async def build_context(db: AsyncSession, idea_id: str) -> Dict[str, Any]:
        """
        Assembles all relevant context for the target idea and parent project.
        """
        # Fetch the idea
        idea_result = await db.execute(select(Idea).where(Idea.id == idea_id))
        idea = idea_result.scalar_one_or_none()
        if not idea:
            raise ValueError(f"Idea with ID {idea_id} not found.")

        # Fetch the parent project
        project_result = await db.execute(select(Project).where(Project.id == idea.project_id))
        project = project_result.scalar_one_or_none()
        if not project:
            raise ValueError(f"Parent project for idea ID {idea_id} not found.")

        return ContextBuilder.compile_context(idea, project)
