"""
Dataset loader for disease-symptom mappings, training data, and multilingual synonyms.
"""

import csv
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any


class DatasetLoader:
    """Load and manage datasets for the symptom checker system."""

    def __init__(self, data_dir: str = "data"):
        """Initialize dataset loader."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def load_disease_symptoms_csv(self) -> pd.DataFrame:
        """
        Load disease-symptom mappings from CSV.
        
        Returns:
            DataFrame with columns: disease, symptom, weight, description
        """
        csv_path = self.data_dir / "diseases_symptoms.csv"
        if csv_path.exists():
            return pd.read_csv(csv_path)
        return pd.DataFrame()

    def load_training_data_csv(self) -> pd.DataFrame:
        """
        Load patient training data from CSV.
        
        Returns:
            DataFrame with patient records and symptom presence/severity
        """
        csv_path = self.data_dir / "training_data.csv"
        if csv_path.exists():
            return pd.read_csv(csv_path)
        return pd.DataFrame()

    def load_multilingual_symptoms_json(self) -> Dict[str, Any]:
        """
        Load multilingual symptom synonyms from JSON.
        
        Returns:
            Dict with symptom names and their translations/synonyms
        """
        json_path = self.data_dir / "multilingual_symptoms.json"
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_disease_symptom_matrix(self) -> Tuple[List[str], List[str], Dict[Tuple[str, str], float]]:
        """
        Get disease-symptom matrix with weights.
        
        Returns:
            Tuple of (diseases, symptoms, weight_dict)
        """
        df = self.load_disease_symptoms_csv()
        if df.empty:
            return [], [], {}

        diseases = sorted(df['disease'].unique().tolist())
        symptoms = sorted(df['symptom'].unique().tolist())
        
        weights = {}
        for _, row in df.iterrows():
            weights[(row['disease'], row['symptom'])] = row['weight']
        
        return diseases, symptoms, weights

    def get_symptom_synonyms(self) -> Dict[str, List[str]]:
        """
        Extract all symptom synonyms across all languages.
        
        Returns:
            Dict mapping symptom_id to list of all synonyms
        """
        data = self.load_multilingual_symptoms_json()
        synonyms = {}
        
        if 'multilingual_symptoms' in data:
            for symptom_id, variants in data['multilingual_symptoms'].items():
                all_variants = []
                for language, terms in variants.items():
                    all_variants.extend(terms)
                synonyms[symptom_id] = all_variants
        
        return synonyms

    def add_disease_symptom_record(self, disease: str, symptom: str, 
                                    weight: float, description: str = "") -> None:
        """
        Add a new disease-symptom mapping.
        
        Args:
            disease: Disease name
            symptom: Symptom ID
            weight: Weight/importance (0-1)
            description: Optional description
        """
        csv_path = self.data_dir / "diseases_symptoms.csv"
        
        # Read existing data
        if csv_path.exists():
            df = pd.read_csv(csv_path)
        else:
            df = pd.DataFrame(columns=['disease', 'symptom', 'weight', 'description'])
        
        # Add new record
        new_record = pd.DataFrame({
            'disease': [disease],
            'symptom': [symptom],
            'weight': [weight],
            'description': [description]
        })
        df = pd.concat([df, new_record], ignore_index=True)
        df.to_csv(csv_path, index=False)

    def add_training_record(self, record: Dict[str, Any]) -> None:
        """
        Add a new patient training record.
        
        Args:
            record: Dict with patient data including symptoms and disease label
        """
        csv_path = self.data_dir / "training_data.csv"
        
        # Read existing data
        if csv_path.exists():
            df = pd.read_csv(csv_path)
        else:
            df = pd.DataFrame()
        
        # Add new record
        new_record = pd.DataFrame([record])
        df = pd.concat([df, new_record], ignore_index=True)
        df.to_csv(csv_path, index=False)

    def add_multilingual_variant(self, symptom_id: str, language: str, variants: List[str]) -> None:
        """
        Add multilingual variants for a symptom.
        
        Args:
            symptom_id: Symptom identifier
            language: Language code (e.g., 'hindi', 'telugu')
            variants: List of symptom terms in that language
        """
        json_path = self.data_dir / "multilingual_symptoms.json"
        
        # Load existing data
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {'multilingual_symptoms': {}}
        
        # Add or update symptom
        if symptom_id not in data['multilingual_symptoms']:
            data['multilingual_symptoms'][symptom_id] = {}
        
        data['multilingual_symptoms'][symptom_id][language] = variants
        
        # Save back
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def export_to_format(self, format_type: str = 'csv', output_dir: str = 'exports') -> None:
        """
        Export datasets to different formats.
        
        Args:
            format_type: 'csv', 'json', 'xlsx'
            output_dir: Directory to export to
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        if format_type in ['csv', 'all']:
            self.load_disease_symptoms_csv().to_csv(
                output_path / 'diseases_symptoms.csv', index=False
            )
            self.load_training_data_csv().to_csv(
                output_path / 'training_data.csv', index=False
            )
        
        if format_type in ['json', 'all']:
            with open(output_path / 'multilingual_symptoms.json', 'w', encoding='utf-8') as f:
                json.dump(self.load_multilingual_symptoms_json(), f, ensure_ascii=False, indent=2)
        
        if format_type in ['xlsx', 'all']:
            with pd.ExcelWriter(output_path / 'symptom_checker_data.xlsx') as writer:
                self.load_disease_symptoms_csv().to_excel(
                    writer, sheet_name='disease_symptoms', index=False
                )
                self.load_training_data_csv().to_excel(
                    writer, sheet_name='training_data', index=False
                )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about loaded datasets.
        
        Returns:
            Dict with dataset statistics
        """
        disease_df = self.load_disease_symptoms_csv()
        training_df = self.load_training_data_csv()
        multilingual = self.load_multilingual_symptoms_json()
        
        stats = {
            'disease_symptom_records': len(disease_df),
            'unique_diseases': len(disease_df['disease'].unique()) if not disease_df.empty else 0,
            'unique_symptoms': len(disease_df['symptom'].unique()) if not disease_df.empty else 0,
            'training_records': len(training_df),
            'multilingual_symptoms': len(multilingual.get('multilingual_symptoms', {})),
            'languages': set(),
        }
        
        # Count languages
        for symptom_data in multilingual.get('multilingual_symptoms', {}).values():
            stats['languages'].update(symptom_data.keys())
        
        stats['languages'] = sorted(list(stats['languages']))
        
        return stats


# Convenience functions
def load_all_data(data_dir: str = "data") -> Dict[str, Any]:
    """Load all datasets at once."""
    loader = DatasetLoader(data_dir)
    return {
        'disease_symptoms': loader.load_disease_symptoms_csv(),
        'training_data': loader.load_training_data_csv(),
        'multilingual': loader.load_multilingual_symptoms_json(),
        'statistics': loader.get_statistics(),
    }


if __name__ == "__main__":
    # Example usage
    loader = DatasetLoader("data")
    
    print("Dataset Statistics:")
    stats = loader.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\nDisease-Symptom Records:")
    print(loader.load_disease_symptoms_csv())
    
    print("\nTraining Data Sample:")
    print(loader.load_training_data_csv().head())
    
    print("\nMultilingual Symptoms:")
    multilingual = loader.load_multilingual_symptoms_json()
    if multilingual:
        for symptom in list(multilingual.get('multilingual_symptoms', {}).keys())[:3]:
            print(f"  {symptom}: {multilingual['multilingual_symptoms'][symptom]}")
