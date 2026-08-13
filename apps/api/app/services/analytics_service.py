from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.project import Project
from app.models.idea import Idea
from app.models.evaluation import Evaluation
from app.schemas.analytics_schema import (
    AnalyticsResponse,
    AnalyticsSummary,
    ProjectMetrics,
    IdeaMetrics,
    EvaluationMetrics,
    ReportMetrics,
    TrendPoint
)

class AnalyticsService:

    @staticmethod
    async def get_user_analytics(
        db: AsyncSession,
        user_id: int,
        time_range: str = "all",
        project_id: Optional[str] = None
    ) -> AnalyticsResponse:
        # Determine Date Cutoff
        now = datetime.now(timezone.utc)
        start_date: Optional[datetime] = None
        if time_range == "7d":
            start_date = now - timedelta(days=7)
        elif time_range == "30d":
            start_date = now - timedelta(days=30)
        elif time_range == "90d":
            start_date = now - timedelta(days=90)
        elif time_range == "1y":
            start_date = now - timedelta(days=365)

        # Base Filters
        proj_conditions = [Project.user_id == user_id, Project.deleted_at.is_(None)]
        if project_id:
            proj_conditions.append(Project.id == project_id)

        # 1. Fetch User Projects
        proj_stmt = select(Project).where(and_(*proj_conditions))
        proj_rows = (await db.execute(proj_stmt)).scalars().all()
        user_project_ids = [p.id for p in proj_rows]

        filtered_projects = [
            p for p in proj_rows
            if not start_date or (p.created_at and p.created_at.replace(tzinfo=timezone.utc) >= start_date)
        ]

        total_projects = len(filtered_projects)
        active_projects = sum(1 for p in filtered_projects if p.status == "active" or p.status == "draft")

        by_status: Dict[str, int] = {}
        by_category: Dict[str, int] = {}
        for p in filtered_projects:
            st = p.status or "draft"
            by_status[st] = by_status.get(st, 0) + 1
            cat = p.category or "Uncategorized"
            by_category[cat] = by_category.get(cat, 0) + 1

        project_metrics = ProjectMetrics(
            total=total_projects,
            by_status=by_status,
            by_category=by_category
        )

        # 2. Fetch User Ideas
        if not user_project_ids:
            ideas_rows: List[Idea] = []
        else:
            idea_stmt = select(Idea).where(Idea.project_id.in_(user_project_ids))
            ideas_rows = (await db.execute(idea_stmt)).scalars().all()

        filtered_ideas = [
            i for i in ideas_rows
            if not start_date or (i.created_at and i.created_at.replace(tzinfo=timezone.utc) >= start_date)
        ]

        total_ideas = len(filtered_ideas)
        draft_ideas = sum(1 for i in filtered_ideas if i.is_draft)
        published_ideas = total_ideas - draft_ideas
        avg_ideas_per_proj = round(total_ideas / max(total_projects, 1), 2) if total_projects > 0 else 0.0

        idea_metrics = IdeaMetrics(
            total=total_ideas,
            drafts=draft_ideas,
            published=published_ideas,
            average_per_project=avg_ideas_per_proj
        )

        # 3. Fetch User Evaluations
        user_idea_ids = [i.id for i in ideas_rows]
        if not user_idea_ids:
            eval_rows: List[Evaluation] = []
        else:
            eval_stmt = select(Evaluation).where(Evaluation.idea_id.in_(user_idea_ids))
            eval_rows = (await db.execute(eval_stmt)).scalars().all()

        filtered_evals = [
            e for e in eval_rows
            if not start_date or (e.created_at and e.created_at.replace(tzinfo=timezone.utc) >= start_date)
        ]

        total_evals = len(filtered_evals)
        completed_evals = [e for e in filtered_evals if e.status == "COMPLETED"]
        failed_evals = sum(1 for e in filtered_evals if e.status == "FAILED")
        cancelled_evals = sum(1 for e in filtered_evals if e.status == "CANCELLED")

        # Score & Dimension Statistics
        overall_scores: List[float] = []
        score_bins = {"0-50": 0, "51-70": 0, "71-85": 0, "86-100": 0}
        dimension_sums: Dict[str, float] = {}
        dimension_counts: Dict[str, int] = {}

        for e in completed_evals:
            payload = e.result_payload or {}
            score = payload.get("overall_score") if payload.get("overall_score") is not None else payload.get("score")
            if score is not None and isinstance(score, (int, float)):
                overall_scores.append(float(score))
                if score <= 50:
                    score_bins["0-50"] += 1
                elif score <= 70:
                    score_bins["51-70"] += 1
                elif score <= 85:
                    score_bins["71-85"] += 1
                else:
                    score_bins["86-100"] += 1

            dims = payload.get("dimensions", {})
            if isinstance(dims, dict):
                for d_key, d_val in dims.items():
                    if isinstance(d_val, (int, float)):
                        dimension_sums[d_key] = dimension_sums.get(d_key, 0.0) + float(d_val)
                        dimension_counts[d_key] = dimension_counts.get(d_key, 0) + 1

        avg_overall_score = round(sum(overall_scores) / len(overall_scores), 1) if overall_scores else None

        dim_averages: Dict[str, float] = {}
        for d_key, d_sum in dimension_sums.items():
            cnt = dimension_counts.get(d_key, 1)
            dim_averages[d_key] = round(d_sum / cnt, 1)

        eval_metrics = EvaluationMetrics(
            total=total_evals,
            completed=len(completed_evals),
            failed=failed_evals,
            cancelled=cancelled_evals,
            average_score=avg_overall_score,
            score_distribution=score_bins,
            dimensional_averages=dim_averages
        )

        # 4. Report Metrics (Safe Fallback)
        report_metrics = ReportMetrics(total=0, by_type={})

        # 5. Build Time-Series Trend
        trend_map: Dict[str, Dict[str, int]] = {}
        
        for p in filtered_projects:
            if p.created_at:
                dt_str = p.created_at.strftime("%Y-%m-%d")
                if dt_str not in trend_map:
                    trend_map[dt_str] = {"projects": 0, "ideas": 0, "evaluations": 0}
                trend_map[dt_str]["projects"] += 1

        for i in filtered_ideas:
            if i.created_at:
                dt_str = i.created_at.strftime("%Y-%m-%d")
                if dt_str not in trend_map:
                    trend_map[dt_str] = {"projects": 0, "ideas": 0, "evaluations": 0}
                trend_map[dt_str]["ideas"] += 1

        for e in filtered_evals:
            if e.created_at:
                dt_str = e.created_at.strftime("%Y-%m-%d")
                if dt_str not in trend_map:
                    trend_map[dt_str] = {"projects": 0, "ideas": 0, "evaluations": 0}
                trend_map[dt_str]["evaluations"] += 1

        sorted_dates = sorted(trend_map.keys())
        trends: List[TrendPoint] = [
            TrendPoint(
                date=d,
                projects_count=trend_map[d]["projects"],
                ideas_count=trend_map[d]["ideas"],
                evaluations_count=trend_map[d]["evaluations"]
            )
            for d in sorted_dates
        ]

        summary = AnalyticsSummary(
            total_projects=total_projects,
            total_ideas=total_ideas,
            total_evaluations=total_evals,
            total_reports=report_metrics.total,
            active_projects=active_projects,
            draft_ideas=draft_ideas,
            completed_evaluations=len(completed_evals),
            average_overall_score=avg_overall_score
        )

        return AnalyticsResponse(
            time_range=time_range,
            summary=summary,
            projects=project_metrics,
            ideas=idea_metrics,
            evaluations=eval_metrics,
            reports=report_metrics,
            trends=trends
        )
