from __future__ import annotations

import pickle
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import numpy as np
from catboost import CatBoostClassifier

from .symptom_catalog import DISEASES, SYMPTOMS


class DiseaseModelService:
    def __init__(self) -> None:
        self.model_path = Path(__file__).resolve().parents[2] / "models" / "catboost_disease.cbm"
        self.retrained_model_path = Path(__file__).resolve().parents[2] / "disease_model_15k.pkl"
        self.model = CatBoostClassifier()
        self._is_fitted = False
        self._retrained_model: Optional[Dict[str, Any]] = None
        self._load_if_exists()

    def _load_if_exists(self) -> None:
        """Try to load retrained model first, then fall back to original model"""
        # Try to load retrained pickle model (15 diseases, 97% accuracy)
        if self.retrained_model_path.exists():
            try:
                with open(self.retrained_model_path, 'rb') as f:
                    self._retrained_model = pickle.load(f)
                self._is_fitted = True
                print(f"✓ Loaded retrained model: {self.retrained_model_path.name}")
                return
            except Exception as e:
                print(f"⚠️  Error loading retrained model: {e}")
        
        # Fall back to original CatBoost model
        if self.model_path.exists():
            try:
                self.model.load_model(str(self.model_path))
                self._is_fitted = True
                print(f"✓ Loaded original model: {self.model_path.name}")
            except Exception as e:
                print(f"⚠️  Error loading original model: {e}")

    def predict(self, features: np.ndarray, detected_symptoms: List[str]) -> Tuple[str, float, List[Dict[str, float]]]:
        if self._retrained_model:
            # Use retrained model (15 diseases, 97% accuracy)
            return self._predict_with_retrained(features, detected_symptoms)
        elif self._is_fitted:
            # Use original model
            probs = self.model.predict_proba(features)[0]
            labels = list(self.model.classes_)
        else:
            # Use rule-based fallback
            probs, labels = self._rule_based_probabilities(features, detected_symptoms)

        pairs = sorted(
            [{"disease": label, "score": float(prob)} for label, prob in zip(labels, probs)],
            key=lambda x: x["score"],
            reverse=True,
        )

        best = pairs[0]
        top_k = [{p["disease"]: round(p["score"], 4)} for p in pairs[:3]]
        return str(best["disease"]), float(best["score"]), top_k

    def _predict_with_retrained(self, features: np.ndarray, detected_symptoms: List[str]) -> Tuple[str, float, List[Dict[str, float]]]:
        """Make predictions using the retrained model"""
        try:
            model = self._retrained_model['model']
            label_encoder = self._retrained_model['label_encoder']
            
            # Get predictions
            probs = model.predict_proba(features)[0]
            labels = label_encoder.classes_
            
            pairs = sorted(
                [{"disease": str(label), "score": float(prob)} for label, prob in zip(labels, probs)],
                key=lambda x: x["score"],
                reverse=True,
            )
            
            best = pairs[0]
            top_k = [{p["disease"]: round(p["score"], 4)} for p in pairs[:3]]
            return str(best["disease"]), float(best["score"]), top_k
        
        except Exception as e:
            print(f"Error in retrained model prediction: {e}")
            # Fall back to rule-based
            probs, labels = self._rule_based_probabilities(features, detected_symptoms)
            pairs = sorted(
                [{"disease": label, "score": float(prob)} for label, prob in zip(labels, probs)],
                key=lambda x: x["score"],
                reverse=True,
            )
            best = pairs[0]
            top_k = [{p["disease"]: round(p["score"], 4)} for p in pairs[:3]]
            return str(best["disease"]), float(best["score"]), top_k

    def _rule_based_probabilities(self, features: np.ndarray, detected_symptoms: List[str]) -> Tuple[np.ndarray, List[str]]:
        score_map = {d: 0.05 for d in DISEASES}
        has = set(detected_symptoms)

        if {"cough", "fever", "sore_throat"}.intersection(has):
            score_map["Influenza"] += 0.25
            score_map["Common Cold"] += 0.2

        if {"cough", "fever", "loss_of_taste_smell", "shortness_of_breath"}.intersection(has):
            score_map["COVID-19"] += 0.35

        if {"vomiting", "diarrhea", "abdominal_pain", "nausea"}.intersection(has):
            score_map["Gastroenteritis"] += 0.45

        if {"headache", "nausea", "blurred_vision"}.intersection(has):
            score_map["Migraine"] += 0.3

        if {"high_blood_sugar", "frequent_urination", "blurred_vision", "fatigue"}.intersection(has):
            score_map["Type 2 Diabetes Alert"] += 0.4

        if len(has) == 0:
            score_map["Common Cold"] += 0.2

        raw = np.array([score_map[d] for d in DISEASES], dtype=np.float32)
        probs = raw / raw.sum()
        return probs, DISEASES


def build_training_dataframe() -> Tuple[np.ndarray, np.ndarray]:
    X: List[List[float]] = []
    y: List[str] = []

    def row(active: List[str], label: str) -> None:
        arr = [0.0] * len(SYMPTOMS)
        for symptom in active:
            arr[SYMPTOMS.index(symptom)] = 1.0
        X.append(arr)
        y.append(label)

    row(["cough", "fever", "runny_nose", "sore_throat"], "Influenza")
    row(["runny_nose", "cough", "sore_throat"], "Common Cold")
    row(["cough", "fever", "loss_of_taste_smell", "shortness_of_breath"], "COVID-19")
    row(["nausea", "vomiting", "diarrhea", "abdominal_pain"], "Gastroenteritis")
    row(["headache", "nausea", "blurred_vision"], "Migraine")
    row(["high_blood_sugar", "frequent_urination", "blurred_vision", "fatigue"], "Type 2 Diabetes Alert")

    row(["fever", "body_pain", "fatigue"], "Influenza")
    row(["cough", "runny_nose"], "Common Cold")
    row(["fever", "cough", "fatigue", "shortness_of_breath"], "COVID-19")
    row(["diarrhea", "abdominal_pain"], "Gastroenteritis")
    row(["headache", "vomiting"], "Migraine")
    row(["high_blood_sugar", "fatigue"], "Type 2 Diabetes Alert")

    return np.array(X, dtype=np.float32), np.array(y)


def train_and_save_model(output_path: Path) -> None:
    X, y = build_training_dataframe()
    model = CatBoostClassifier(
        iterations=180,
        depth=6,
        learning_rate=0.08,
        loss_function="MultiClass",
        random_seed=42,
        verbose=False,
    )
    model.fit(X, y)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(str(output_path))
