from __future__ import annotations

from typing import Dict, List

from .symptom_catalog import DISEASE_BASELINE_SEVERITY


class RiskAwareLayer:
    def score(
        self,
        predicted_disease: str,
        confidence: float,
        intensity: Dict[str, float],
        detected_symptoms: List[str],
    ) -> Dict[str, float | str]:
        baseline = DISEASE_BASELINE_SEVERITY.get(predicted_disease, 0.3)
        avg_intensity = sum(intensity.values()) / max(len(intensity), 1) if intensity else 0.4
        burden = min(len(detected_symptoms) / 8.0, 1.0)

        risk_score = 0.45 * baseline + 0.35 * confidence + 0.2 * ((avg_intensity + burden) / 2)
        risk_score = max(0.0, min(1.0, risk_score))

        if risk_score < 0.3:
            level = "Low"
        elif risk_score < 0.5:
            level = "Moderate"
        elif risk_score < 0.75:
            level = "High"
        else:
            level = "Critical"

        return {"risk_level": level, "risk_score": round(risk_score, 4)}
