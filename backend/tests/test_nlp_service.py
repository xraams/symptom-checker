import pytest
import numpy as np
from app.services.nlp_service import BiomedicalNLPService
from app.services.symptom_catalog import SYMPTOMS


class TestBiomedicalNLPService:
    def test_initialization(self, nlp_service):
        assert nlp_service is not None
        assert len(nlp_service._compiled) > 0

    def test_normalize_text(self, nlp_service):
        result = nlp_service.normalize_text("  Hello   WORLD  ")
        assert result == "hello world"

    def test_extract_symptoms_english(self, nlp_service):
        text = "I have fever and cough"
        symptoms = nlp_service.extract_symptoms(text)
        assert "fever" in symptoms
        assert "cough" in symptoms

    def test_extract_symptoms_multiple(self, nlp_service):
        text = "fever, cough, sore throat, headache"
        symptoms = nlp_service.extract_symptoms(text)
        assert len(symptoms) >= 3
        assert "fever" in symptoms
        assert "cough" in symptoms

    def test_extract_symptoms_case_insensitive(self, nlp_service):
        text_lower = "fever and cough"
        text_upper = "FEVER AND COUGH"
        symptoms_lower = nlp_service.extract_symptoms(text_lower)
        symptoms_upper = nlp_service.extract_symptoms(text_upper)
        assert symptoms_lower == symptoms_upper

    def test_extract_symptoms_no_match(self, nlp_service):
        text = "xyz abc qwerty"
        symptoms = nlp_service.extract_symptoms(text)
        assert len(symptoms) == 0

    def test_extract_symptoms_transliterated_hindi(self, nlp_service):
        text = "mujhe bukhar aur khansi hai"
        symptoms = nlp_service.extract_symptoms(text)
        assert "fever" in symptoms
        assert "cough" in symptoms

    def test_extract_symptoms_transliterated_hindi2(self, nlp_service):
        text = "gale dard"
        symptoms = nlp_service.extract_symptoms(text)
        assert "sore_throat" in symptoms

    def test_build_feature_vector_shape(self, nlp_service):
        text = "fever and cough"
        features, detected = nlp_service.build_feature_vector(text, {})
        assert features.shape == (1, len(SYMPTOMS))
        assert isinstance(features, np.ndarray)

    def test_build_feature_vector_detected_symptoms(self, nlp_service):
        text = "I have fever and cough"
        features, detected = nlp_service.build_feature_vector(text, {})
        assert "fever" in detected
        assert "cough" in detected

    def test_build_feature_vector_with_intensity(self, nlp_service):
        text = "fever"
        intensity = {"fever": 0.9, "cough": 0.7}
        features, detected = nlp_service.build_feature_vector(text, intensity)
        fever_idx = SYMPTOMS.index("fever")
        cough_idx = SYMPTOMS.index("cough")
        assert features[0, fever_idx] >= 0.9
        assert features[0, cough_idx] >= 0.7

    def test_build_feature_vector_intensity_bounds(self, nlp_service):
        text = "fever"
        intensity = {"fever": 10.0, "cough": -5.0}
        features, detected = nlp_service.build_feature_vector(text, intensity)
        assert np.all(features >= 0.0)
        assert np.all(features <= 1.0)

    def test_feature_vector_values_normalized(self, nlp_service):
        text = "fever, cough, sore throat"
        features, _ = nlp_service.build_feature_vector(text, {})
        assert np.all(features >= 0.0)
        assert np.all(features <= 1.0)
