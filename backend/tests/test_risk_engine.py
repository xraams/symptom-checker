import pytest
from app.services.risk_engine import RiskAwareLayer


class TestRiskAwareLayer:
    def test_initialization(self, risk_layer):
        assert risk_layer is not None

    def test_score_returns_dict(self, risk_layer):
        result = risk_layer.score("Common Cold", 0.5, {}, ["fever"])
        assert isinstance(result, dict)
        assert "risk_level" in result
        assert "risk_score" in result

    def test_score_risk_levels(self, risk_layer):
        valid_levels = {"Low", "Moderate", "High", "Critical"}
        for disease in ["Common Cold", "Influenza", "COVID-19"]:
            result = risk_layer.score(disease, 0.5, {}, ["fever"])
            assert result["risk_level"] in valid_levels

    def test_score_risk_score_in_range(self, risk_layer):
        result = risk_layer.score("Influenza", 0.8, {"fever": 0.9}, ["fever", "cough"])
        assert 0.0 <= result["risk_score"] <= 1.0

    def test_score_low_risk(self, risk_layer):
        result = risk_layer.score("Common Cold", 0.2, {"fever": 0.1}, ["runny_nose"])
        assert result["risk_level"] == "Low"
        assert result["risk_score"] < 0.3

    def test_score_high_risk(self, risk_layer):
        result = risk_layer.score("COVID-19", 0.9, {"fever": 0.9, "cough": 0.9}, ["fever", "cough", "shortness_of_breath"])
        assert result["risk_level"] in {"High", "Critical"}

    def test_score_critical_risk(self, risk_layer):
        result = risk_layer.score("COVID-19", 0.95, {"fever": 1.0, "cough": 1.0}, ["fever", "cough", "shortness_of_breath", "chest_pain"])
        assert result["risk_level"] == "Critical"

    def test_score_moderate_risk(self, risk_layer):
        result = risk_layer.score("Influenza", 0.5, {"fever": 0.5}, ["fever"])
        assert result["risk_level"] in {"Low", "Moderate"}

    def test_score_increasing_with_confidence(self, risk_layer):
        low_conf = risk_layer.score("Influenza", 0.3, {}, ["fever"])
        high_conf = risk_layer.score("Influenza", 0.8, {}, ["fever"])
        assert high_conf["risk_score"] >= low_conf["risk_score"]

    def test_score_increasing_with_intensity(self, risk_layer):
        low_intensity = risk_layer.score("Influenza", 0.5, {"fever": 0.2}, ["fever"])
        high_intensity = risk_layer.score("Influenza", 0.5, {"fever": 0.9}, ["fever"])
        assert high_intensity["risk_score"] >= low_intensity["risk_score"]

    def test_score_empty_symptoms(self, risk_layer):
        result = risk_layer.score("Common Cold", 0.4, {}, [])
        assert result["risk_level"] in {"Low", "Moderate", "High", "Critical"}

    def test_score_type_2_diabetes(self, risk_layer):
        result = risk_layer.score("Type 2 Diabetes Alert", 0.7, {"high_blood_sugar": 0.8}, ["high_blood_sugar"])
        assert result["risk_level"] in {"Low", "Moderate", "High", "Critical"}
