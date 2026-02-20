"""
FastAPI endpoints for feedback collection
Add these endpoints to the main app
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import json
from pathlib import Path

router = APIRouter(prefix="/feedback", tags=["Feedback"])

# Models for feedback
class PredictionFeedback(BaseModel):
    prediction_id: str
    actual_disease: str
    predicted_disease: str
    confidence: float
    user_comment: Optional[str] = None
    user_id: Optional[str] = None

class FeatureRequest(BaseModel):
    feature: str
    description: str
    user_id: Optional[str] = None

class BugReport(BaseModel):
    bug_description: str
    severity: str  # "critical", "high", "medium", "low"
    steps_to_reproduce: Optional[str] = None
    device_info: Optional[str] = None

# In-memory storage (use database in production)
feedback_data = {
    "predictions": [],
    "features": [],
    "bugs": []
}

@router.post("/prediction")
async def submit_prediction_feedback(feedback: PredictionFeedback):
    """
    Submit feedback on a prediction
    
    Example:
    ```json
    {
      "prediction_id": "pred_001",
      "actual_disease": "Flu",
      "predicted_disease": "Hypertension",
      "confidence": 0.58,
      "user_comment": "Actually had the flu, not hypertension"
    }
    ```
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        **feedback.dict()
    }
    feedback_data["predictions"].append(entry)
    
    # Save to file
    _save_feedback_to_file()
    
    return {
        "status": "success",
        "message": "Thank you for your feedback! This helps us improve the model.",
        "feedback_id": f"fb_{len(feedback_data['predictions'])}"
    }

@router.post("/feature-request")
async def submit_feature_request(request: FeatureRequest):
    """
    Submit a feature request
    
    Example:
    ```json
    {
      "feature": "Multilingual Support",
      "description": "Add Spanish and Portuguese language support"
    }
    ```
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        **request.dict(),
        "votes": 1
    }
    feedback_data["features"].append(entry)
    _save_feedback_to_file()
    
    return {
        "status": "success",
        "message": "Feature request submitted! We appreciate your suggestions."
    }

@router.post("/bug-report")
async def submit_bug_report(report: BugReport):
    """
    Submit a bug report
    
    Example:
    ```json
    {
      "bug_description": "App crashes on some devices",
      "severity": "critical",
      "steps_to_reproduce": "Use on Android 9 devices",
      "device_info": "Samsung Galaxy S9, Android 9"
    }
    ```
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        **report.dict(),
        "status": "new"
    }
    feedback_data["bugs"].append(entry)
    _save_feedback_to_file()
    
    return {
        "status": "success",
        "message": "Bug report submitted. Thank you for helping us improve!",
        "ticket_id": f"bug_{len(feedback_data['bugs'])}"
    }

@router.get("/stats")
async def get_feedback_stats():
    """Get feedback statistics (admin endpoint)"""
    
    # Calculate accuracy from prediction feedback
    predictions = feedback_data["predictions"]
    if predictions:
        correct = sum(1 for p in predictions 
                     if p["actual_disease"].lower() == p["predicted_disease"].lower())
        accuracy = (correct / len(predictions)) * 100
    else:
        accuracy = 0
    
    return {
        "total_predictions_feedback": len(predictions),
        "model_accuracy_from_feedback": f"{accuracy:.1f}%",
        "total_feature_requests": len(feedback_data["features"]),
        "total_bug_reports": len(feedback_data["bugs"]),
        "last_updated": datetime.now().isoformat()
    }

def _save_feedback_to_file():
    """Save feedback to JSON file"""
    feedback_file = Path("feedback_data.json")
    try:
        with open(feedback_file, 'w') as f:
            json.dump(feedback_data, f, indent=2)
    except Exception as e:
        print(f"Error saving feedback: {e}")

# Usage in main.py:
# from .feedback_endpoints import router as feedback_router
# app.include_router(feedback_router)
