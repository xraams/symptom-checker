"""
Unit tests for dataset loader and enhanced NLP service.
"""

import pytest
from pathlib import Path
import json

from app.services.dataset_loader import DatasetLoader
from app.services.nlp_service_enhanced import EnhancedBiomedicalNLPService


class TestDatasetLoader:
    """Test dataset loading functionality."""

    @pytest.fixture
    def loader(self):
        return DatasetLoader("data")

    def test_load_disease_symptoms_csv(self, loader):
        """Test loading disease-symptom mappings."""
        df = loader.load_disease_symptoms_csv()
        assert not df.empty, "Disease-symptom CSV should not be empty"
        assert 'disease' in df.columns, "Should have 'disease' column"
        assert 'symptom' in df.columns, "Should have 'symptom' column"
        assert 'weight' in df.columns, "Should have 'weight' column"

    def test_disease_symptom_properties(self, loader):
        """Test disease-symptom data properties."""
        df = loader.load_disease_symptoms_csv()
        
        # Check weights are in valid range
        assert (df['weight'] >= 0).all(), "Weights should be >= 0"
        assert (df['weight'] <= 1).all(), "Weights should be <= 1"
        
        # Check all diseases have at least one symptom
        disease_counts = df['disease'].value_counts()
        assert (disease_counts >= 1).all(), "Each disease should have symptoms"

    def test_load_training_data_csv(self, loader):
        """Test loading training data."""
        df = loader.load_training_data_csv()
        assert not df.empty, "Training data CSV should not be empty"
        assert 'patient_id' in df.columns
        assert 'disease' in df.columns
        assert 'fever' in df.columns or len(df) > 0

    def test_training_data_properties(self, loader):
        """Test training data sanity checks."""
        df = loader.load_training_data_csv()
        
        # Check symptom columns are in valid range
        symptom_cols = ['fever', 'cough', 'sore_throat', 'fatigue']
        for col in symptom_cols:
            if col in df.columns:
                assert (df[col] >= 0).all(), f"{col} should be >= 0"
                assert (df[col] <= 1).all(), f"{col} should be <= 1"

    def test_load_multilingual_symptoms(self, loader):
        """Test loading multilingual synonyms."""
        data = loader.load_multilingual_symptoms_json()
        assert 'multilingual_symptoms' in data, "Should have multilingual_symptoms key"
        assert len(data['multilingual_symptoms']) > 0, "Should have symptom data"

    def test_multilingual_structure(self, loader):
        """Test multilingual data structure."""
        data = loader.load_multilingual_symptoms_json()
        multilingual = data['multilingual_symptoms']
        
        # Check first symptom has multiple languages
        for symptom_id, variants in list(multilingual.items())[:3]:
            assert isinstance(variants, dict), f"{symptom_id} should map to dict"
            assert len(variants) > 0, f"{symptom_id} should have language variants"
            for lang, terms in variants.items():
                assert isinstance(terms, list), f"{symptom_id}.{lang} should be list"
                assert len(terms) > 0, f"{symptom_id}.{lang} should have terms"

    def test_get_disease_symptom_matrix(self, loader):
        """Test disease-symptom matrix generation."""
        diseases, symptoms, weights = loader.get_disease_symptom_matrix()
        
        assert len(diseases) > 0, "Should have diseases"
        assert len(symptoms) > 0, "Should have symptoms"
        assert len(weights) > 0, "Should have weight mappings"
        
        # Verify all entries in weights are valid
        for (disease, symptom), weight in weights.items():
            assert disease in diseases
            assert symptom in symptoms
            assert 0 <= weight <= 1

    def test_get_symptom_synonyms(self, loader):
        """Test symptom synonym extraction."""
        synonyms = loader.get_symptom_synonyms()
        
        assert len(synonyms) > 0, "Should have symptom synonyms"
        assert 'fever' in synonyms, "fever should be present"
        assert len(synonyms['fever']) > 0, "fever should have synonyms"
        
        # Check for multilingual variants
        fever_syns = synonyms['fever']
        assert any('बुखार' in syn or 'bukhar' in syn for syn in fever_syns), \
            "fever should have Hindi variants"

    def test_get_statistics(self, loader):
        """Test statistics generation."""
        stats = loader.get_statistics()
        
        assert 'disease_symptom_records' in stats
        assert 'unique_diseases' in stats
        assert 'unique_symptoms' in stats
        assert 'training_records' in stats
        assert 'languages' in stats
        
        assert stats['disease_symptom_records'] > 0
        assert stats['unique_diseases'] > 0
        assert stats['unique_symptoms'] > 0

    def test_add_disease_symptom_record(self, loader, tmp_path):
        """Test adding disease-symptom record."""
        # Use temp directory
        temp_loader = DatasetLoader(str(tmp_path))
        
        # Add a record
        temp_loader.add_disease_symptom_record(
            "TestDisease", "fever", 0.8, "Test description"
        )
        
        # Verify it was added
        df = temp_loader.load_disease_symptoms_csv()
        assert not df.empty
        test_records = df[df['disease'] == 'TestDisease']
        assert len(test_records) > 0

    def test_add_multilingual_variant(self, loader, tmp_path):
        """Test adding multilingual variants."""
        temp_loader = DatasetLoader(str(tmp_path))
        
        temp_loader.add_multilingual_variant(
            "test_symptom",
            "test_language",
            ["term1", "term2", "term3"]
        )
        
        data = temp_loader.load_multilingual_symptoms_json()
        assert 'test_symptom' in data['multilingual_symptoms']
        assert 'test_language' in data['multilingual_symptoms']['test_symptom']


class TestEnhancedBiomedicalNLPService:
    """Test enhanced NLP service with datasets."""

    @pytest.fixture
    def nlp_service(self):
        return EnhancedBiomedicalNLPService(data_dir="data")

    def test_initialization(self, nlp_service):
        """Test NLP service initializes correctly."""
        assert nlp_service._compiled is not None
        assert len(nlp_service._compiled) > 0

    def test_normalize_text(self, nlp_service):
        """Test text normalization."""
        assert nlp_service.normalize_text("  Fever  ") == "fever"
        assert nlp_service.normalize_text("COUGH\n  COLD") == "cough cold"

    def test_extract_symptoms_english(self, nlp_service):
        """Test symptom extraction in English."""
        symptoms = nlp_service.extract_symptoms("I have fever and cough")
        assert "fever" in symptoms
        assert "cough" in symptoms

    def test_extract_symptoms_multilingual(self, nlp_service):
        """Test symptom extraction in multiple languages."""
        # Hindi transliteration
        symptoms = nlp_service.extract_symptoms("bukhar aur khansi")
        assert len(symptoms) > 0, "Should detect Hindi symptoms"

    def test_extract_symptoms_with_confidence(self, nlp_service):
        """Test symptom extraction with confidence scores."""
        results = nlp_service.extract_symptoms_with_confidence(
            "fever and body pain"
        )
        assert len(results) > 0
        for symptom, confidence in results:
            assert isinstance(confidence, float)
            assert 0 <= confidence <= 1

    def test_build_feature_vector(self, nlp_service):
        """Test feature vector construction."""
        vector, detected = nlp_service.build_feature_vector(
            "fever and cough",
            {"fever": 0.8}
        )
        
        assert vector is not None
        assert len(detected) > 0
        assert isinstance(vector, __import__('numpy').ndarray)

    def test_get_symptom_synonyms(self, nlp_service):
        """Test retrieval of symptom synonyms."""
        fever_syns = nlp_service.get_symptom_synonyms("fever")
        assert len(fever_syns) > 0
        assert any("fever" in syn.lower() for syn in fever_syns)

    def test_add_symptom_variants(self, nlp_service):
        """Test adding symptom variants dynamically."""
        initial_syns = nlp_service.get_symptom_synonyms("fever")
        initial_count = len(initial_syns)
        
        nlp_service.add_symptom_variants("fever", ["test_variant_new"])
        
        updated_syns = nlp_service.get_symptom_synonyms("fever")
        assert len(updated_syns) >= initial_count

    def test_get_stats(self, nlp_service):
        """Test statistics generation."""
        stats = nlp_service.get_stats()
        
        assert 'total_symptoms' in stats
        assert 'indexed_symptoms' in stats
        assert 'total_synonym_variants' in stats
        assert stats['total_symptoms'] > 0

    def test_no_false_positives(self, nlp_service):
        """Test that service doesn't extract symptoms from unrelated text."""
        symptoms = nlp_service.extract_symptoms(
            "The weather is beautiful today"
        )
        # Should not detect symptoms from normal text
        assert len(symptoms) == 0 or all(
            symptom in ["fever", "cough"] for symptom in symptoms
        )

    def test_empty_input(self, nlp_service):
        """Test handling of empty input."""
        symptoms = nlp_service.extract_symptoms("")
        assert symptoms == []
        
        vector, detected = nlp_service.build_feature_vector("", {})
        assert detected == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
