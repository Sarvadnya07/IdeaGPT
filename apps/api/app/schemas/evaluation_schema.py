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
