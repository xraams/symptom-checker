"""
Retrain CatBoost model with expanded 15000-record dataset.
"""

import pandas as pd
import numpy as np
from catboost import CatBoostClassifier
import pickle
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from typing import Tuple


class ModelRetrainer:
    """Retrain disease prediction model with new dataset."""

    def __init__(self, data_dir: str = "data", model_path: str = "disease_model.pkl"):
        self.data_dir = Path(data_dir)
        self.model_path = Path(model_path)
        self.model = None
        self.label_encoder = LabelEncoder()
        self.feature_columns = None

    def load_training_data(self) -> pd.DataFrame:
        """Load the processed training dataset."""
        train_file = self.data_dir / 'training_data_15k.csv'
        print(f"Loading training data from {train_file}...")
        df = pd.read_csv(train_file)
        print(f"✓ Loaded {len(df)} training records")
        print(f"✓ Features: {len(df.columns)} columns")
        return df

    def prepare_features_and_labels(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, list]:
        """
        Prepare feature matrix and labels.
        
        Returns:
            Tuple of (X, y, feature_names)
        """
        # Remove non-feature columns
        exclude_cols = {'patient_id', 'disease', 'text'}
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        X = df[feature_cols].values.astype(np.float32)
        y = df['disease'].values
        
        self.feature_columns = feature_cols
        
        print(f"\n✓ Features: {len(feature_cols)}")
        print(f"✓ Training samples: {X.shape[0]}")
        print(f"✓ Classes (diseases): {len(np.unique(y))}")
        print(f"  {sorted(np.unique(y).tolist())}")
        
        return X, y, feature_cols

    def train_model(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train CatBoost model.
        
        Args:
            X: Feature matrix
            y: Labels (disease names)
        """
        print("\n" + "="*80)
        print("TRAINING CATBOOST MODEL")
        print("="*80)
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        print(f"\nTraining/Test Split:")
        print(f"  Train: {X_train.shape[0]} samples")
        print(f"  Test: {X_test.shape[0]} samples")
        
        # Initialize and train model
        print(f"\nTraining CatBoost classifier...")
        self.model = CatBoostClassifier(
            iterations=500,
            learning_rate=0.05,
            depth=8,
            loss_function='MultiClass',
            eval_metric='MultiClass',
            verbose=False,
            random_state=42,
            thread_count=-1,  # Use all CPU cores
        )
        
        self.model.fit(
            X_train, y_train,
            eval_set=(X_test, y_test),
            early_stopping_rounds=50,
            verbose=False,
        )
        
        # Evaluate
        train_accuracy = self.model.score(X_train, y_train)
        test_accuracy = self.model.score(X_test, y_test)
        
        print(f"\n✓ Model trained!")
        print(f"  Training Accuracy: {train_accuracy:.4f}")
        print(f"  Test Accuracy: {test_accuracy:.4f}")
        
        return train_accuracy, test_accuracy

    def get_feature_importance(self, top_n: int = 15) -> pd.DataFrame:
        """Get feature importance."""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        importances = self.model.get_feature_importance()
        feature_importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        return feature_importance_df

    def save_model(self) -> None:
        """Save trained model to disk."""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        print(f"\nSaving model to {self.model_path}...")
        
        model_data = {
            'model': self.model,
            'label_encoder': self.label_encoder,
            'feature_columns': self.feature_columns,
        }
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✓ Model saved to {self.model_path}")
        print(f"✓ File size: {self.model_path.stat().st_size / 1024 / 1024:.2f} MB")

    def print_summary(self, train_acc: float, test_acc: float) -> None:
        """Print training summary."""
        print("\n" + "="*80)
        print("MODEL RETRAINING SUMMARY")
        print("="*80)
        print(f"\nTraining Data:")
        print(f"  Source: merged_symptom_dataset_15000.csv")
        print(f"  Records: 15,000")
        print(f"  Features: {len(self.feature_columns)}")
        print(f"  Diseases: {len(self.label_encoder.classes_)}")
        
        print(f"\nModel Configuration:")
        print(f"  Algorithm: CatBoost")
        print(f"  Iterations: 500")
        print(f"  Learning Rate: 0.05")
        print(f"  Tree Depth: 8")
        
        print(f"\nPerformance:")
        print(f"  Training Accuracy: {train_acc:.4f}")
        print(f"  Test Accuracy: {test_acc:.4f}")
        
        print(f"\nClasses Supported:")
        diseases = sorted(self.label_encoder.classes_.tolist())
        for i, disease in enumerate(diseases, 1):
            print(f"  {i:2d}. {disease}")
        
        print(f"\nTop 10 Important Features:")
        top_features = self.get_feature_importance(10)
        for idx, row in top_features.iterrows():
            print(f"  {row['feature']:.<30} {row['importance']:.4f}")
        
        print("\n" + "="*80)


def retrain_model():
    """Main retraining pipeline."""
    import os
    
    # Check if training data exists
    if not Path("data/training_data_15k.csv").exists():
        print("❌ Training data not found!")
        print("   Run: python integrate_dataset.py data/merged_symptom_dataset_15000.csv")
        return
    
    # Initialize retrainer
    retrainer = ModelRetrainer(data_dir="data", model_path="disease_model_15k.pkl")
    
    # Load and prepare data
    df = retrainer.load_training_data()
    X, y, features = retrainer.prepare_features_and_labels(df)
    
    # Train model
    train_acc, test_acc = retrainer.train_model(X, y)
    
    # Save model
    retrainer.save_model()
    
    # Print summary
    retrainer.print_summary(train_acc, test_acc)
    
    print("\n✅ Model retraining complete!")
    print("   Updated model: disease_model_15k.pkl")
    return retrainer


if __name__ == "__main__":
    retrain_model()
