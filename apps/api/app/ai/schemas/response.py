from pydantic import BaseModel, Field, conint, confloat
from typing import List, Dict, Any, Optional

class DimensionScores(BaseModel):
    innovation: conint(ge=0, le=100) = Field(..., description="Originality, defense, gap potential")
    market_potential: conint(ge=0, le=100) = Field(..., description="TAM/SAM/SOM, market fit")
    technical_feasibility: conint(ge=0, le=100) = Field(..., description="Complexity, dev timeline, risks")
    business_viability: conint(ge=0, le=100) = Field(..., description="Revenue model, customer acquisition")
    scalability: conint(ge=0, le=100) = Field(..., description="Ops leverage, scalability boundaries")
    execution_complexity: conint(ge=0, le=100) = Field(..., description="Dev timeline complexity")
    competitive_differentiation: conint(ge=0, le=100) = Field(..., description="Market gap defense")

class AIResponseModel(BaseModel):
    summary: str = Field(..., description="High level executive summary of the evaluation")
    score: conint(ge=0, le=100) = Field(..., description="Overall calculated score derived dynamically")
    strengths: List[str] = Field(default_factory=list, description="List of key strengths")
    weaknesses: List[str] = Field(default_factory=list, description="List of key weaknesses")
    recommendations: List[str] = Field(default_factory=list, description="List of structured suggestions")
    confidence: confloat(ge=0.0, le=1.0) = Field(..., description="AI confidence index")
    dimensions: DimensionScores = Field(..., description="Detailed dimension scoring")
    architecture_breakdown: Optional[str] = Field(None, description="Detailed markdown containing architectural plan")
