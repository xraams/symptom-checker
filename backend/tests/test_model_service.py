import pytest
import numpy as np
from app.services.model_service import DiseaseModelService
from app.services.symptom_catalog import DISEASES


class TestDiseaseModelService:
    def test_initialization(self, model_service):
        assert model_service is not None

    def test_predict_returns_tuple(self, model_service):
        features = np.random.rand(1, 18).astype(np.float32)
        disease, confidence, top_k = model_service.predict(features, [])
        assert isinstance(disease, str)
        assert isinstance(confidence, float)
        assert isinstance(top_k, list)

    def test_predict_confidence_in_range(self, model_service):
        features = np.random.rand(1, 18).astype(np.float32)
        disease, confidence, top_k = model_service.predict(features, [])
        assert 0.0 <= confidence <= 1.0

    def test_predict_disease_in_catalog(self, model_service):
        features = np.random.rand(1, 18).astype(np.float32)
        disease, confidence, top_k = model_service.predict(features, [])
        assert disease in DISEASES

    def test_predict_top_k_format(self, model_service):
        features = np.random.rand(1, 18).astype(np.float32)
        disease, confidence, top_k = model_service.predict(features, [])
        assert len(top_k) > 0
        assert all(isinstance(item, dict) for item in top_k)

    def test_predict_fever_symptoms_influenza(self, model_service):
        features = np.zeros((1, 18), dtype=np.float32)
        features[0, 0] = 0.8  # fever
        disease, confidence, _ = model_service.predict(features, ["fever"])
        assert disease in DISEASES

    def test_predict_covid_symptoms_detected(self, model_service):
        features = np.zeros((1, 18), dtype=np.float32)
        features[0, 0] = 0.8  # fever
        features[0, 1] = 0.8  # cough
        features[0, 14] = 0.8  # loss_of_taste_smell
        disease, confidence, _ = model_service.predict(features, ["fever", "cough", "loss_of_taste_smell"])
        assert disease in DISEASES

    def test_predict_gastro_symptoms(self, model_service):
        features = np.zeros((1, 18), dtype=np.float32)
        features[0, 7] = 0.8  # vomiting
        features[0, 8] = 0.8  # diarrhea
        features[0, 9] = 0.8  # abdominal_pain
        disease, confidence, _ = model_service.predict(features, ["vomiting", "diarrhea", "abdominal_pain"])
        assert disease in DISEASES

    def test_predict_empty_features(self, model_service):
        features = np.zeros((1, 18), dtype=np.float32)
        disease, confidence, top_k = model_service.predict(features, [])
        assert disease in DISEASES
        assert confidence > 0.0

    def test_predict_all_ones(self, model_service):
        features = np.ones((1, 18), dtype=np.float32)
        disease, confidence, top_k = model_service.predict(features, [])
        assert disease in DISEASES
        assert 0.0 < confidence <= 1.0
