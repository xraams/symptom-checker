import pytest
import numpy as np
from app.services.explainability import IntegratedGradientsExplainer
from app.services.symptom_catalog import SYMPTOMS


class TestIntegratedGradientsExplainer:
    def test_initialization(self, explainer):
        assert explainer is not None

    def test_explain_returns_list(self, explainer):
        features = np.random.rand(1, 18).astype(np.float32)
        explanations = explainer.explain(features, ["fever", "cough"])
        assert isinstance(explanations, list)

    def test_explain_contributions_in_range(self, explainer):
        features = np.random.rand(1, 18).astype(np.float32)
        explanations = explainer.explain(features, ["fever"])
        for item in explanations:
            assert 0.0 <= item["contribution"] <= 1.0

    def test_explain_symptom_names_valid(self, explainer):
        features = np.random.rand(1, 18).astype(np.float32)
        explanations = explainer.explain(features, ["fever", "cough"])
        for item in explanations:
            assert item["symptom"] in SYMPTOMS

    def test_explain_detected_symptoms_included(self, explainer):
        features = np.zeros((1, 18), dtype=np.float32)
        features[0, 0] = 0.9  # fever
        detected = ["fever"]
        explanations = explainer.explain(features, detected)
        symptom_names = [e["symptom"] for e in explanations]
        assert "fever" in symptom_names

    def test_explain_max_8_items(self, explainer):
        features = np.ones((1, 18), dtype=np.float32)
        explanations = explainer.explain(features, [])
        assert len(explanations) <= 8

    def test_explain_sorted_by_contribution(self, explainer):
        features = np.random.rand(1, 18).astype(np.float32)
        explanations = explainer.explain(features, [])
        if len(explanations) > 1:
            for i in range(len(explanations) - 1):
                assert explanations[i]["contribution"] >= explanations[i + 1]["contribution"]

    def test_explain_zero_features(self, explainer):
        features = np.zeros((1, 18), dtype=np.float32)
        explanations = explainer.explain(features, [])
        assert isinstance(explanations, list)

    def test_explain_high_intensity_features(self, explainer):
        features = np.ones((1, 18), dtype=np.float32)
        explanations = explainer.explain(features, [])
        assert len(explanations) > 0
        max_contribution = max(e["contribution"] for e in explanations)
        assert max_contribution > 0.0
