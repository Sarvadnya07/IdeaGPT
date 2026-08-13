from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class EvaluationCreate(BaseModel):
    evaluation_type: Optional[str] = "startup_evaluation"

class EvaluationResponse(BaseModel):
    id: str
    project_id: str
    idea_id: str
    provider: Optional[str] = None
    model: Optional[str] = None
    evaluation_type: str
    status: str
    progress: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    token_usage: Optional[int] = None
    estimated_cost: Optional[float] = None
    error_message: Optional[str] = None
    result_payload: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EvaluationHistoryResponse(BaseModel):
    id: str
    evaluation_id: str
    event_type: str
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    progress: Optional[str] = None
    message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class IdeaCompareRequest(BaseModel):
    idea_ids: List[str]

class IdeaComparisonItem(BaseModel):
    idea_id: str
    project_id: str
    title: str
    problem_statement: Optional[str] = None
    solution_description: Optional[str] = None
    target_users: Optional[str] = None
    industry: Optional[str] = None
    business_model: Optional[str] = None
    stage: Optional[str] = None
    tags: Optional[str] = None
    completeness_score: int
    evaluation_status: str  # "evaluated" | "unevaluated"
    evaluation_id: Optional[str] = None
    overall_score: Optional[int] = None
    score_delta: Optional[int] = None
    rank: Optional[int] = None
    dimensions: Dict[str, Any] = {}
    evaluated_at: Optional[str] = None

class IdeaComparisonResponse(BaseModel):
    compared_count: int
    highest_score_idea_id: Optional[str] = None
    ideas: List[IdeaComparisonItem]
    dimension_labels: Dict[str, str] = {
        "innovation": "Innovation",
        "market_potential": "Market Potential",
        "execution_complexity": "Execution Complexity",
        "technical_feasibility": "Technical Feasibility",
        "business_viability": "Business Viability",
        "scalability": "Scalability",
        "competitive_differentiation": "Competitive Differentiation"
    }
