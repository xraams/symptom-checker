"""
Model Loader - Handles loading both retrained (pickle) and original (CatBoost) models
Automatically detects and loads the best available model
"""

import pickle
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np


class ModelLoader:
    """Load and manage disease prediction models"""
    
    @staticmethod
    def load_retrained_model() -> Optional[Dict[str, Any]]:
        """
        Load the retrained model from pickle format
        Returns: Dictionary with 'model', 'label_encoder', 'feature_columns'
        Returns None if model not found
        """
        model_path = Path(__file__).resolve().parents[2] / "disease_model_15k.pkl"
        
        if not model_path.exists():
            return None
        
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # Verify structure
            required_keys = {'model', 'label_encoder', 'feature_columns'}
            if required_keys.issubset(model_data.keys()):
                print(f"✓ Loaded retrained model: {model_path.name}")
                return model_data
        except Exception as e:
            print(f"⚠️ Error loading retrained model: {e}")
        
        return None
    
    @staticmethod
    def get_available_diseases(model_data: Dict[str, Any]) -> list:
        """Get list of diseases the model can predict"""
        if 'label_encoder' in model_data:
            return list(model_data['label_encoder'].classes_)
        return []
    
    @staticmethod
    def get_feature_columns(model_data: Dict[str, Any]) -> list:
        """Get feature column names used by the model"""
        if 'feature_columns' in model_data:
            return model_data['feature_columns']
        return []
    
    @staticmethod
    def predict_with_model(model_data: Dict[str, Any], features: np.ndarray) -> tuple:
        """
        Make predictions with the loaded model
        Returns: (predicted_disease, confidence, disease_probabilities)
        """
        try:
            model = model_data['model']
            label_encoder = model_data['label_encoder']
            
            # Get predictions
            probs = model.predict_proba(features)[0]
            predicted_idx = np.argmax(probs)
            predicted_disease = label_encoder.classes_[predicted_idx]
            confidence = float(probs[predicted_idx])
            
            # Create top-k results
            top_indices = np.argsort(-probs)[:3]
            top_diseases = {
                label_encoder.classes_[idx]: float(probs[idx]) 
                for idx in top_indices
            }
            
            return predicted_disease, confidence, top_diseases
        
        except Exception as e:
            print(f"⚠️ Error during prediction: {e}")
            raise
