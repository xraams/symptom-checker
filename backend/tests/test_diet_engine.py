import pytest
from app.services.diet_engine import NutrientScoredLayer


class TestNutrientScoredLayer:
    def test_initialization(self, diet_layer):
        assert diet_layer is not None

    def test_recommend_returns_dict(self, diet_layer):
        result = diet_layer.recommend("Common Cold", "Low")
        assert isinstance(result, dict)
        assert "recommended" in result
        assert "avoid" in result
        assert "notes" in result

    def test_recommend_fields_are_lists(self, diet_layer):
        result = diet_layer.recommend("Influenza", "Moderate")
        assert isinstance(result["recommended"], list)
        assert isinstance(result["avoid"], list)
        assert isinstance(result["notes"], list)

    def test_recommend_common_cold(self, diet_layer):
        result = diet_layer.recommend("Common Cold", "Low")
        assert len(result["recommended"]) > 0
        assert len(result["avoid"]) > 0
        assert any("soup" in item.lower() or "citrus" in item.lower() or "ginger" in item.lower() 
                   for item in result["recommended"])

    def test_recommend_influenza(self, diet_layer):
        result = diet_layer.recommend("Influenza", "Moderate")
        assert len(result["recommended"]) > 0
        assert any("electrolyte" in item.lower() or "oats" in item.lower() 
                   for item in result["recommended"])

    def test_recommend_covid(self, diet_layer):
        result = diet_layer.recommend("COVID-19", "High")
        assert len(result["recommended"]) > 0
        assert "Easily digestible meals" in result["recommended"]

    def test_recommend_gastroenteritis(self, diet_layer):
        result = diet_layer.recommend("Gastroenteritis", "Moderate")
        assert any("ors" in item.lower() or "banana" in item.lower() or "rice" in item.lower() 
                   for item in result["recommended"])

    def test_recommend_migraine(self, diet_layer):
        result = diet_layer.recommend("Migraine", "Low")
        assert len(result["recommended"]) > 0

    def test_recommend_diabetes(self, diet_layer):
        result = diet_layer.recommend("Type 2 Diabetes Alert", "Moderate")
        assert any("low-gi" in item.lower() or "legume" in item.lower() 
                   for item in result["recommended"])

    def test_recommend_high_risk_adjustments(self, diet_layer):
        low_risk = diet_layer.recommend("Influenza", "Low")
        high_risk = diet_layer.recommend("Influenza", "High")
        assert len(high_risk["recommended"]) > len(low_risk["recommended"])
        assert any("easily" in item.lower() for item in high_risk["recommended"])
        assert any("medical" in item.lower() for item in high_risk["notes"])

    def test_recommend_critical_risk(self, diet_layer):
        result = diet_layer.recommend("COVID-19", "Critical")
        assert "Easily digestible meals" in result["recommended"]
        assert any("medical" in item.lower() for item in result["notes"])

    def test_recommend_unknown_disease(self, diet_layer):
        result = diet_layer.recommend("Unknown Disease", "Moderate")
        assert len(result["recommended"]) > 0
        assert len(result["avoid"]) > 0
        assert any("dietitian" in item.lower() for item in result["notes"])
