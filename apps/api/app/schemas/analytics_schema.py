from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class AnalyticsSummary(BaseModel):
    total_projects: int = 0
    total_ideas: int = 0
    total_evaluations: int = 0
    total_reports: int = 0
    active_projects: int = 0
    draft_ideas: int = 0
    completed_evaluations: int = 0
    average_overall_score: Optional[float] = None

class ProjectMetrics(BaseModel):
    total: int = 0
    by_status: Dict[str, int] = Field(default_factory=dict)
    by_category: Dict[str, int] = Field(default_factory=dict)

class IdeaMetrics(BaseModel):
    total: int = 0
    drafts: int = 0
    published: int = 0
    average_per_project: float = 0.0

class EvaluationMetrics(BaseModel):
    total: int = 0
    completed: int = 0
    failed: int = 0
    cancelled: int = 0
    average_score: Optional[float] = None
    score_distribution: Dict[str, int] = Field(
        default_factory=lambda: {"0-50": 0, "51-70": 0, "71-85": 0, "86-100": 0}
    )
    dimensional_averages: Dict[str, float] = Field(default_factory=dict)

class ReportMetrics(BaseModel):
    total: int = 0
    by_type: Dict[str, int] = Field(default_factory=dict)

class TrendPoint(BaseModel):
    date: str
    projects_count: int = 0
    ideas_count: int = 0
    evaluations_count: int = 0

class AnalyticsResponse(BaseModel):
    time_range: str
    summary: AnalyticsSummary
    projects: ProjectMetrics
    ideas: IdeaMetrics
    evaluations: EvaluationMetrics
    reports: ReportMetrics
    trends: List[TrendPoint] = Field(default_factory=list)
