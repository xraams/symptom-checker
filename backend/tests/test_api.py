import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_status_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestPredictEndpoint:
    def test_predict_empty_text(self, client):
        payload = {
            "language": "en",
            "text": "",
            "symptom_intensity": {}
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422

    def test_predict_english_basic(self, client):
        payload = {
            "language": "en",
            "text": "I have fever and cough",
            "symptom_intensity": {"fever": 0.8, "cough": 0.7}
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "predicted_disease" in data
        assert "confidence" in data
        assert "risk_level" in data

    def test_predict_response_structure(self, client):
        payload = {
            "language": "en",
            "text": "fever and cough",
            "symptom_intensity": {}
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        required_fields = [
            "predicted_disease",
            "confidence",
            "top_k",
            "risk_level",
            "risk_score",
            "explainability",
            "detected_symptoms",
            "diet"
        ]
        for field in required_fields:
            assert field in data

    def test_predict_confidence_range(self, client):
        payload = {
            "language": "en",
            "text": "fever",
            "symptom_intensity": {"fever": 0.9}
        }
        response = client.post("/predict", json=payload)
        data = response.json()
        assert 0.0 <= data["confidence"] <= 1.0

    def test_predict_risk_level_valid(self, client):
        payload = {
            "language": "en",
            "text": "high fever and severe cough",
            "symptom_intensity": {"fever": 0.9, "cough": 0.9}
        }
        response = client.post("/predict", json=payload)
        data = response.json()
        assert data["risk_level"] in {"Low", "Moderate", "High", "Critical"}

    def test_predict_explainability_present(self, client):
        payload = {
            "language": "en",
            "text": "fever cough headache",
            "symptom_intensity": {}
        }
        response = client.post("/predict", json=payload)
        data = response.json()
        assert len(data["explainability"]) > 0
        for item in data["explainability"]:
            assert "symptom" in item
            assert "contribution" in item

    def test_predict_diet_structure(self, client):
        payload = {
            "language": "en",
            "text": "fever",
            "symptom_intensity": {}
        }
        response = client.post("/predict", json=payload)
        data = response.json()
        diet = data["diet"]
        assert "recommended" in diet
        assert "avoid" in diet
        assert "notes" in diet
        assert len(diet["recommended"]) > 0

    def test_predict_detected_symptoms_matches_input(self, client):
        payload = {
            "language": "en",
            "text": "I have fever, cough, and sore throat",
            "symptom_intensity": {}
        }
        response = client.post("/predict", json=payload)
        data = response.json()
        detected = data["detected_symptoms"]
        assert "fever" in detected
        assert "cough" in detected
        assert "sore_throat" in detected

    def test_predict_multiple_calls_consistency(self, client):
        payload = {
            "language": "en",
            "text": "fever and cough",
            "symptom_intensity": {"fever": 0.8, "cough": 0.7}
        }
        response1 = client.post("/predict", json=payload)
        response2 = client.post("/predict", json=payload)
        data1 = response1.json()
        data2 = response2.json()
        assert data1["predicted_disease"] == data2["predicted_disease"]
        assert abs(data1["confidence"] - data2["confidence"]) < 0.01

    def test_predict_with_high_intensity(self, client):
        payload = {
            "language": "en",
            "text": "fever",
            "symptom_intensity": {"fever": 0.95}
        }
        response = client.post("/predict", json=payload)
        data = response.json()
        assert data["risk_score"] > 0.0

    def test_predict_top_k_present(self, client):
        payload = {
            "language": "en",
            "text": "fever and cough",
            "symptom_intensity": {}
        }
        response = client.post("/predict", json=payload)
        data = response.json()
        assert len(data["top_k"]) > 0
        assert all(isinstance(item, dict) for item in data["top_k"])
