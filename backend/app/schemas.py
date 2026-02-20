from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    user_id: Optional[str] = None
    language: str = Field(default="en", description="ISO-like code: en, hi, te")
    text: str = Field(..., min_length=2)
    symptom_intensity: Dict[str, float] = Field(default_factory=dict)


class ExplainItem(BaseModel):
    symptom: str
    contribution: float


class DietPlan(BaseModel):
    recommended: List[str]
    avoid: List[str]
    notes: List[str]


class PredictResponse(BaseModel):
    predicted_disease: str
    confidence: float
    top_k: List[Dict[str, float]]
    risk_level: str
    risk_score: float
    explainability: List[ExplainItem]
    detected_symptoms: List[str]
    diet: DietPlan
