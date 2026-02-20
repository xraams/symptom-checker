"""
Utility script to manage and update datasets.
Usage: python manage_datasets.py [command] [args]
"""

import sys
import json
from pathlib import Path
from app.services.dataset_loader import DatasetLoader


def print_datasets():
    """Print all loaded datasets."""
    loader = DatasetLoader("data")
    
    print("\n" + "="*80)
    print("DATASET STATISTICS")
    print("="*80)
    stats = loader.get_statistics()
    for key, value in stats.items():
        print(f"{key:.<40} {value}")
    
    print("\n" + "="*80)
    print("DISEASE-SYMPTOM MAPPINGS")
    print("="*80)
    df = loader.load_disease_symptoms_csv()
    if not df.empty:
        for disease in df['disease'].unique():
            symptoms = df[df['disease'] == disease][['symptom', 'weight']].to_dict('records')
            print(f"\n{disease}:")
            for s in symptoms:
                print(f"  - {s['symptom']}: {s['weight']}")
    
    print("\n" + "="*80)
    print("TRAINING DATA SAMPLE")
    print("="*80)
    training_df = loader.load_training_data_csv()
    if not training_df.empty:
        print(f"Total records: {len(training_df)}")
        print("\nFirst 5 records:")
        print(training_df[['patient_id', 'disease', 'fever', 'cough', 'sore_throat', 'duration_days']].head())
    
    print("\n" + "="*80)
    print("MULTILINGUAL SYMPTOMS")
    print("="*80)
    multilingual = loader.load_multilingual_symptoms_json()
    if multilingual:
        for symptom_id in list(multilingual.get('multilingual_symptoms', {}).keys())[:5]:
            data = multilingual['multilingual_symptoms'][symptom_id]
            print(f"\n{symptom_id}:")
            for lang, terms in data.items():
                print(f"  {lang}: {terms[:2]}...")


def add_disease(disease: str, symptom: str, weight: float, description: str = ""):
    """Add a new disease-symptom mapping."""
    loader = DatasetLoader("data")
    loader.add_disease_symptom_record(disease, symptom, weight, description)
    print(f"✓ Added mapping: {disease} -> {symptom} (weight: {weight})")


def add_language_variants(symptom_id: str, language: str, variants_json: str):
    """Add multilingual variants for a symptom."""
    loader = DatasetLoader("data")
    variants = json.loads(variants_json)
    loader.add_multilingual_variant(symptom_id, language, variants)
    print(f"✓ Added {language} variants for {symptom_id}")


def export_data(format_type: str = 'csv'):
    """Export datasets to specified format."""
    loader = DatasetLoader("data")
    loader.export_to_format(format_type, "exports")
    print(f"✓ Exported data to {format_type} format in 'exports/' directory")


def help_message():
    """Print help message."""
    print("""
Dataset Management Commands:

  python manage_datasets.py show
    Display all loaded datasets and statistics

  python manage_datasets.py add-disease <disease> <symptom> <weight> [description]
    Add a new disease-symptom mapping
    Example: python manage_datasets.py add-disease "Asthma" "shortness_of_breath" 0.9

  python manage_datasets.py add-language <symptom_id> <language> '<json_array>'
    Add multilingual variants for a symptom
    Example: python manage_datasets.py add-language "fever" "french" '["fievre", "temperature"]'

  python manage_datasets.py export <format>
    Export datasets (csv, json, xlsx, all)
    Example: python manage_datasets.py export all

  python manage_datasets.py help
    Show this help message
    """)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        help_message()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'show':
        print_datasets()
    elif command == 'add-disease':
        if len(sys.argv) < 5:
            print("Usage: add-disease <disease> <symptom> <weight> [description]")
            return
        disease = sys.argv[2]
        symptom = sys.argv[3]
        weight = float(sys.argv[4])
        description = sys.argv[5] if len(sys.argv) > 5 else ""
        add_disease(disease, symptom, weight, description)
    elif command == 'add-language':
        if len(sys.argv) < 5:
            print("Usage: add-language <symptom_id> <language> '<json_array>'")
            return
        symptom_id = sys.argv[2]
        language = sys.argv[3]
        variants_json = sys.argv[4]
        add_language_variants(symptom_id, language, variants_json)
    elif command == 'export':
        format_type = sys.argv[2] if len(sys.argv) > 2 else 'csv'
        export_data(format_type)
    elif command == 'help':
        help_message()
    else:
        print(f"Unknown command: {command}")
        help_message()


if __name__ == "__main__":
    main()
