from __future__ import annotations

from typing import Dict, List

import numpy as np

from .symptom_catalog import SYMPTOMS


class IntegratedGradientsExplainer:
    def _catboost_like_score(self, x: np.ndarray) -> float:
        return float(np.clip(x.mean() + 0.35 * x.max(), 0.0, 1.0))

    def explain(self, features: np.ndarray, detected_symptoms: List[str]) -> List[Dict[str, float]]:
        x = features[0]
        baseline = np.zeros_like(x)
        steps = 30

        attributions = np.zeros_like(x)
        for i in range(1, steps + 1):
            alpha = i / steps
            x_alpha = baseline + alpha * (x - baseline)
            grad_approx = np.where(x_alpha > 0, 1.0 / (len(x_alpha) + 1e-6), 0.0)
            attributions += grad_approx

        attributions = (x - baseline) * attributions / steps

        items: List[Dict[str, float]] = []
        for idx, symptom in enumerate(SYMPTOMS):
            val = float(attributions[idx])
            if symptom in detected_symptoms or val > 0.01:
                items.append({"symptom": symptom, "contribution": round(val, 4)})

        items.sort(key=lambda it: it["contribution"], reverse=True)
        return items[:8]
