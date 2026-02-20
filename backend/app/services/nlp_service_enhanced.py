"""
Enhanced NLP service with dynamic multilingual dataset support.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple, Optional
import numpy as np

from .symptom_catalog import SYMPTOMS
from .dataset_loader import DatasetLoader


class EnhancedBiomedicalNLPService:
    """
    NLP service with support for dynamic multilingual datasets.
    Falls back to static catalog if datasets unavailable.
    """

    def __init__(self, data_dir: Optional[str] = None) -> None:
        """
        Initialize enhanced NLP service.
        
        Args:
            data_dir: Path to data directory. If None, uses default 'data/'
        """
        self.data_dir = data_dir or "data"
        self._compiled: Dict[str, List[re.Pattern[str]]] = {}
        self._multilingual_synonyms: Dict[str, List[str]] = {}
        
        # Try to load from datasets
        try:
            self._load_from_datasets()
        except Exception as e:
            print(f"Warning: Could not load datasets: {e}")
            self._load_from_static_catalog()

    def _load_from_datasets(self) -> None:
        """Load synonyms from dataset files."""
        loader = DatasetLoader(self.data_dir)
        self._multilingual_synonyms = loader.get_symptom_synonyms()
        self._compile_patterns()

    def _load_from_static_catalog(self) -> None:
        """Fall back to static symptom catalog."""
        from .symptom_catalog import SYMPTOM_SYNONYMS
        self._multilingual_synonyms = {
            symptom: synonyms for symptom, synonyms in SYMPTOM_SYNONYMS.items()
        }
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex patterns for all symptom synonyms."""
        self._compiled = {}
        for symptom, synonyms in self._multilingual_synonyms.items():
            if symptom in SYMPTOMS:
                self._compiled[symptom] = [
                    self._compile_term(term) for term in synonyms
                ]

    def _compile_term(self, term: str) -> re.Pattern[str]:
        """
        Compile a single term into a regex pattern.
        Uses word boundaries for ASCII terms, simple matching for Unicode.
        """
        lowered = term.lower()
        escaped = re.escape(lowered)
        is_ascii = all(ord(char) < 128 for char in lowered)
        if is_ascii:
            return re.compile(rf"\b{escaped}\b")
        return re.compile(escaped)

    def normalize_text(self, text: str) -> str:
        """Normalize text: lowercase, strip, collapse whitespace."""
        return re.sub(r"\s+", " ", text.lower().strip())

    def extract_symptoms(self, text: str) -> List[str]:
        """
        Extract detected symptoms from text.
        
        Args:
            text: User input text (can be multilingual)
            
        Returns:
            List of detected symptom IDs
        """
        cleaned = self.normalize_text(text)
        hits: List[str] = []
        
        for symptom in SYMPTOMS:
            for pattern in self._compiled.get(symptom, []):
                if pattern.search(cleaned):
                    hits.append(symptom)
                    break
        
        return hits

    def extract_symptoms_with_confidence(self, text: str) -> List[Tuple[str, float]]:
        """
        Extract symptoms with confidence scores.
        
        Args:
            text: User input text
            
        Returns:
            List of (symptom, confidence) tuples
        """
        detected = self.extract_symptoms(text)
        # Base confidence based on match
        return [(symptom, 0.8) for symptom in detected]

    def build_feature_vector(
        self, text: str, intensity: Dict[str, float]
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Build feature vector from text and intensity scores.
        
        Args:
            text: User input text
            intensity: Dict mapping symptom IDs to intensity scores (0-1)
            
        Returns:
            Tuple of (feature_vector, detected_symptoms)
        """
        detected = self.extract_symptoms(text)
        feature_map = {symptom: 0.0 for symptom in SYMPTOMS}

        # Base score from text extraction
        for symptom in detected:
            feature_map[symptom] = max(feature_map[symptom], 0.6)

        # Override with explicit intensity scores
        for symptom, score in intensity.items():
            if symptom in feature_map:
                clipped = float(min(max(score, 0.0), 1.0))
                feature_map[symptom] = max(feature_map[symptom], clipped)

        # Create vector
        vector = np.array(
            [feature_map[s] for s in SYMPTOMS], dtype=np.float32
        )

        return vector, detected

    def get_symptom_synonyms(self, symptom: str) -> List[str]:
        """
        Get all known synonyms for a symptom.
        
        Args:
            symptom: Symptom ID
            
        Returns:
            List of synonyms in multiple languages
        """
        return self._multilingual_synonyms.get(symptom, [])

    def add_symptom_variants(self, symptom: str, variants: List[str]) -> None:
        """
        Add new variants for a symptom dynamically.
        
        Args:
            symptom: Symptom ID
            variants: New symptom terms/synonyms
        """
        if symptom not in self._multilingual_synonyms:
            self._multilingual_synonyms[symptom] = []
        
        # Add new variants
        for variant in variants:
            if variant not in self._multilingual_synonyms[symptom]:
                self._multilingual_synonyms[symptom].append(variant)
        
        # Recompile patterns
        self._compile_patterns()

    def get_stats(self) -> Dict[str, int]:
        """Get NLP service statistics."""
        total_synonyms = sum(
            len(syns) for syns in self._multilingual_synonyms.values()
        )
        return {
            'total_symptoms': len(SYMPTOMS),
            'indexed_symptoms': len(self._compiled),
            'total_synonym_variants': total_synonyms,
            'avg_variants_per_symptom': (
                total_synonyms // len(self._compiled) if self._compiled else 0
            ),
        }


# Backward compatibility: export original class name
BiomedicalNLPService = EnhancedBiomedicalNLPService


# Legacy implementation for tests
class _LegacyBiomedicalNLPService:
    """Original implementation using static catalog."""

    def __init__(self) -> None:
        from .symptom_catalog import SYMPTOM_SYNONYMS
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

    def build_feature_vector(
        self, text: str, intensity: Dict[str, float]
    ) -> Tuple[np.ndarray, List[str]]:
        detected = self.extract_symptoms(text)
        feature_map = {symptom: 0.0 for symptom in SYMPTOMS}

        for symptom in detected:
            feature_map[symptom] = max(feature_map[symptom], 0.6)

        for symptom, score in intensity.items():
            if symptom in feature_map:
                clipped = float(min(max(score, 0.0), 1.0))
                feature_map[symptom] = max(feature_map[symptom], clipped)

        vector = np.array(
            [feature_map[s] for s in SYMPTOMS], dtype=np.float32
        )

        return vector, detected
