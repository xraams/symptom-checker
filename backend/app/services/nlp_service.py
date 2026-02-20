from __future__ import annotations

import re
from typing import Dict, List, Tuple

import numpy as np

from .symptom_catalog import SYMPTOM_SYNONYMS, SYMPTOMS


class BiomedicalNLPService:
    def __init__(self) -> None:
        self._compiled = {
            symptom: [self._compile_term(term) for term in synonyms]
            for symptom, synonyms in SYMPTOM_SYNONYMS.items()
        }

    def _compile_term(self, term: str) -> re.Pattern[str]:
        lowered = term.lower()
        escaped = re.escape(lowered)
        is_ascii = all(ord(char) < 128 for char in lowered)
        if is_ascii:
            return re.compile(rf"\b{escaped}\b")
        return re.compile(escaped)

    def normalize_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.lower().strip())

    def extract_symptoms(self, text: str) -> List[str]:
        cleaned = self.normalize_text(text)
        hits: List[str] = []
        for symptom in SYMPTOMS:
            for pattern in self._compiled.get(symptom, []):
                if pattern.search(cleaned):
                    hits.append(symptom)
                    break
        return hits

    def build_feature_vector(self, text: str, intensity: Dict[str, float]) -> Tuple[np.ndarray, List[str]]:
        detected = self.extract_symptoms(text)
        feature_map = {symptom: 0.0 for symptom in SYMPTOMS}

        for symptom in detected:
            feature_map[symptom] = max(feature_map[symptom], 0.6)

        for symptom, score in intensity.items():
            if symptom in feature_map:
                clipped = float(min(max(score, 0.0), 1.0))
                feature_map[symptom] = max(feature_map[symptom], clipped)

        vector = np.array([[feature_map[s] for s in SYMPTOMS]], dtype=np.float32)
        return vector, detected
