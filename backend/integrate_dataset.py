"""
Integration script for large merged symptom dataset (15000 records).
Analyzes, processes, and integrates the dataset into the system.
"""

import pandas as pd
import json
import re
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set


class DatasetIntegration:
    """Integrate and analyze large symptom dataset."""

    def __init__(self, dataset_path: str, data_dir: str = "data"):
        self.dataset_path = Path(dataset_path)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.df = None
        self.disease_symptom_map: Dict[str, Set[str]] = defaultdict(set)

    def load_dataset(self) -> pd.DataFrame:
        """Load the merged dataset."""
        print(f"Loading dataset from {self.dataset_path}...")
        self.df = pd.read_csv(self.dataset_path)
        print(f"✓ Loaded {len(self.df)} records")
        print(f"✓ Columns: {list(self.df.columns)}")
        return self.df

    def get_statistics(self) -> Dict:
        """Get dataset statistics."""
        if self.df is None:
            self.load_dataset()

        diseases = self.df['disease'].nunique()
        records = len(self.df)
        avg_text_length = self.df['text'].str.len().mean()
        
        stats = {
            'total_records': records,
            'unique_diseases': diseases,
            'diseases': sorted(self.df['disease'].unique().tolist()),
            'avg_text_length': round(avg_text_length, 2),
            'disease_distribution': self.df['disease'].value_counts().to_dict(),
        }
        
        return stats

    def extract_symptoms_from_text(self, text: str) -> List[str]:
        """
        Extract symptom terms from text.
        Uses common symptom keywords.
        """
        symptom_keywords = [
            'fever', 'cough', 'cold', 'flu', 'pain', 'ache', 'headache',
            'nausea', 'vomiting', 'diarrhea', 'weakness', 'fatigue',
            'dizziness', 'shortness of breath', 'rash', 'itching',
            'sneezing', 'runny nose', 'eye', 'vision', 'weight loss',
            'thirst', 'chills', 'joint', 'chest', 'stomach', 'blurred',
            'discomfort', 'sensitivity', 'skin', 'discharge', 'sweating',
            'loss of appetite', 'high fever', 'dry', 'productive', 'wheezing',
            'tightness', 'throat', 'congestion', 'inflammation', 'swelling',
            'bleeding', 'red', 'tender', 'stiff', 'numb', 'tingling'
        ]
        
        text_lower = text.lower()
        found = []
        
        for keyword in symptom_keywords:
            if keyword in text_lower:
                found.append(keyword)
        
        return found

    def build_disease_symptom_matrix(self) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """
        Build disease-symptom mapping with weights.
        
        Returns:
            Tuple of (disease_symptom_df, symptom_weights)
        """
        if self.df is None:
            self.load_dataset()

        disease_symptom_records = []
        symptom_counts = Counter()
        
        for _, row in self.df.iterrows():
            disease = row['disease']
            text = row['text']
            symptoms = self.extract_symptoms_from_text(text)
            
            for symptom in symptoms:
                self.disease_symptom_map[disease].add(symptom)
                symptom_counts[symptom] += 1
                disease_symptom_records.append({
                    'disease': disease,
                    'symptom': symptom,
                })
        
        # Convert to DataFrame
        disease_symptom_df = pd.DataFrame(disease_symptom_records)
        
        if not disease_symptom_df.empty:
            # Add weights based on frequency
            disease_symptom_df = disease_symptom_df.drop_duplicates(
                subset=['disease', 'symptom']
            )
            
            # Calculate weights
            total_symptoms = len(symptom_counts)
            weights = {s: count / total_symptoms for s, count in symptom_counts.items()}
            
            disease_symptom_df['weight'] = disease_symptom_df['symptom'].map(weights)
            disease_symptom_df['description'] = disease_symptom_df['symptom']
        
        return disease_symptom_df, symptom_counts

    def create_training_dataset(self) -> pd.DataFrame:
        """
        Create structured training dataset with symptom features.
        """
        if self.df is None:
            self.load_dataset()
        
        # Get all unique symptoms
        all_symptoms = set()
        for symptoms in self.disease_symptom_map.values():
            all_symptoms.update(symptoms)
        
        all_symptoms = sorted(list(all_symptoms))
        print(f"\nFound {len(all_symptoms)} unique symptoms:")
        print(f"  {', '.join(all_symptoms[:20])}...")
        
        # Create feature vectors
        training_records = []
        
        for idx, row in self.df.iterrows():
            disease = row['disease']
            text = row['text']
            symptoms = set(self.extract_symptoms_from_text(text))
            
            record = {
                'patient_id': f'P{idx:05d}',
                'disease': disease,
                'text': text[:100],  # First 100 chars
            }
            
            # Add binary features for each symptom
            for symptom in all_symptoms:
                record[symptom] = 1.0 if symptom in symptoms else 0.0
            
            training_records.append(record)
        
        training_df = pd.DataFrame(training_records)
        print(f"\n✓ Created training dataset with {len(training_df)} records")
        print(f"✓ Features: {len(training_df.columns)} columns")
        
        return training_df

    def update_symptom_catalog(self) -> Dict:
        """
        Update symptom catalog with new diseases and symptoms.
        """
        symptom_keywords = [
            'fever', 'cough', 'cold', 'flu', 'pain', 'ache', 'headache',
            'nausea', 'vomiting', 'diarrhea', 'weakness', 'fatigue',
            'dizziness', 'shortness_of_breath', 'rash', 'itching',
            'sneezing', 'runny_nose', 'eye_pain', 'blurred_vision', 'weight_loss',
            'increased_thirst', 'chills', 'joint_pain', 'chest_pain', 'stomach_pain',
            'chest_discomfort', 'sensitivity_to_light', 'skin_rash', 'discharge',
            'sweating', 'loss_of_appetite', 'high_fever', 'dry_cough', 'wheezing',
            'chest_tightness', 'sore_throat', 'nasal_congestion'
        ]
        
        catalog = {
            'DISEASES': sorted(list(set(self.df['disease'].tolist()))),
            'SYMPTOMS': symptom_keywords,
            'DISEASE_SYMPTOM_MAP': {
                disease: sorted(list(symptoms))
                for disease, symptoms in self.disease_symptom_map.items()
            }
        }
        
        return catalog

    def save_processed_datasets(self) -> None:
        """Save all processed datasets."""
        print("\nSaving processed datasets...")
        
        # 1. Save disease-symptom mappings
        disease_symptom_df, _ = self.build_disease_symptom_matrix()
        if not disease_symptom_df.empty:
            csv_path = self.data_dir / 'disease_symptom_matrix_15k.csv'
            disease_symptom_df.to_csv(csv_path, index=False)
            print(f"✓ Saved disease-symptom mappings to {csv_path}")
        
        # 2. Save training dataset
        training_df = self.create_training_dataset()
        train_csv = self.data_dir / 'training_data_15k.csv'
        training_df.to_csv(train_csv, index=False)
        print(f"✓ Saved training data to {train_csv}")
        
        # 3. Save updated catalog
        catalog = self.update_symptom_catalog()
        catalog_json = self.data_dir / 'expanded_symptom_catalog.json'
        with open(catalog_json, 'w') as f:
            json.dump(catalog, f, indent=2)
        print(f"✓ Saved symptom catalog to {catalog_json}")
        
        # 4. Save statistics
        stats = self.get_statistics()
        stats_json = self.data_dir / 'dataset_statistics.json'
        with open(stats_json, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        print(f"✓ Saved statistics to {stats_json}")

    def print_summary(self) -> None:
        """Print integration summary."""
        stats = self.get_statistics()
        
        print("\n" + "="*80)
        print("DATASET INTEGRATION SUMMARY")
        print("="*80)
        print(f"\nDataset Size:")
        print(f"  Total Records: {stats['total_records']:,}")
        print(f"  Unique Diseases: {stats['unique_diseases']}")
        print(f"  Average Text Length: {stats['avg_text_length']} chars")
        
        print(f"\nDiseases Found:")
        for disease, count in sorted(stats['disease_distribution'].items(), 
                                     key=lambda x: x[1], reverse=True):
            print(f"  - {disease}: {count} cases")
        
        print(f"\nNew Diseases (not in original catalog):")
        original_diseases = {
            'Common Cold', 'Influenza', 'COVID-19', 
            'Gastroenteritis', 'Migraine', 'Type 2 Diabetes Alert'
        }
        new_diseases = set(stats['diseases']) - original_diseases
        if new_diseases:
            for disease in sorted(new_diseases)[:10]:
                count = stats['disease_distribution'].get(disease, 0)
                print(f"  + {disease}: {count} cases")
            if len(new_diseases) > 10:
                print(f"  ... and {len(new_diseases) - 10} more diseases")
        
        print(f"\nProcessed Datasets:")
        print(f"  ✓ disease_symptom_matrix_15k.csv")
        print(f"  ✓ training_data_15k.csv")
        print(f"  ✓ expanded_symptom_catalog.json")
        print(f"  ✓ dataset_statistics.json")
        print("\n" + "="*80)


if __name__ == "__main__":
    import sys
    
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else \
        "merged_symptom_dataset_15000.csv"
    
    integrator = DatasetIntegration(dataset_path, "data")
    integrator.load_dataset()
    
    # Print statistics
    integrator.print_summary()
    
    # Save processed datasets
    integrator.save_processed_datasets()
    
    print("\n✅ Dataset integration complete!")
    print("   Next step: Retrain CatBoost model with new training data")
