from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import PredictRequest, PredictResponse, ExplainItem, DietPlan
from .services.diet_engine import NutrientScoredLayer
from .services.explainability import IntegratedGradientsExplainer
from .services.model_service import DiseaseModelService
from .services.nlp_service import BiomedicalNLPService
from .services.risk_engine import RiskAwareLayer

app = FastAPI(title="Symptom Checker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nlp_service = BiomedicalNLPService()
model_service = DiseaseModelService()
explainer = IntegratedGradientsExplainer()
risk_layer = RiskAwareLayer()
diet_layer = NutrientScoredLayer()


@app.on_event("startup")
def bootstrap_model() -> None:
    try:
        model_service._load_if_exists()
    except Exception as e:
        print(f"⚠️ Startup model load failed, continuing with fallback mode: {e}")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Input text is required")

    features, detected = nlp_service.build_feature_vector(payload.text, payload.symptom_intensity)
    disease, confidence, top_k = model_service.predict(features, detected)
    explanations = explainer.explain(features, detected)
    risk_data = risk_layer.score(disease, confidence, payload.symptom_intensity, detected)
    diet = diet_layer.recommend(disease, str(risk_data["risk_level"]))

    return PredictResponse(
        predicted_disease=disease,
        confidence=round(confidence, 4),
        top_k=top_k,
        risk_level=str(risk_data["risk_level"]),
        risk_score=float(risk_data["risk_score"]),
        explainability=[ExplainItem(**item) for item in explanations],
        detected_symptoms=detected,
        diet=DietPlan(**diet),
    )
