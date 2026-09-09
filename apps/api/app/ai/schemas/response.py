from pydantic import BaseModel, Field, conint, confloat
from typing import List, Dict, Any, Optional

class DimensionScores(BaseModel):
    innovation: int = Field(..., ge=0, le=100, description="Originality, defense, gap potential")
    market_potential: int = Field(..., ge=0, le=100, description="TAM/SAM/SOM, market fit")
    technical_feasibility: int = Field(..., ge=0, le=100, description="Complexity, dev timeline, risks")
    business_viability: int = Field(..., ge=0, le=100, description="Revenue model, customer acquisition")
    scalability: int = Field(..., ge=0, le=100, description="Ops leverage, scalability boundaries")
    execution_complexity: int = Field(..., ge=0, le=100, description="Dev timeline complexity")
    competitive_differentiation: int = Field(..., ge=0, le=100, description="Market gap defense")

class AIResponseModel(BaseModel):
    summary: str = Field(..., description="High level executive summary of the evaluation")
    score: int = Field(..., ge=0, le=100, description="Overall calculated score derived dynamically")
    strengths: List[str] = Field(default_factory=list, description="List of key strengths")
    weaknesses: List[str] = Field(default_factory=list, description="List of key weaknesses")
    recommendations: List[str] = Field(default_factory=list, description="List of structured suggestions")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence index")
    dimensions: DimensionScores = Field(..., description="Detailed dimension scoring")
    architecture_breakdown: Optional[str] = Field(None, description="Detailed markdown containing architectural plan")

