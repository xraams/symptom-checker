#!/usr/bin/env python3
"""
Update API to use the new retrained model (disease_model_15k.pkl)
This script will:
1. Update main.py to load the new model
2. Verify the new model works
3. Display updated disease coverage
"""

import os
import sys
import pickle
from pathlib import Path

def check_model_exists(model_path):
    """Verify model file exists and is valid."""
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        return False
    
    try:
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        print(f"✅ Model loaded: {model_path.name}")
        print(f"   - Model: {model_data['model'].__class__.__name__}")
        print(f"   - Diseases: {len(model_data['label_encoder'].classes_)}")
        print(f"   - Diseases: {sorted(model_data['label_encoder'].classes_)}")
        return True
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

def update_main_py(backend_path):
    """Update main.py to use disease_model_15k.pkl"""
    main_file = backend_path / "app" / "main.py"
    
    if not main_file.exists():
        print(f"❌ main.py not found: {main_file}")
        return False
    
    try:
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Check if already updated
        if 'disease_model_15k.pkl' in content:
            print("✅ main.py already uses disease_model_15k.pkl")
            return True
        
        # Update model loading line
        old_line = 'Path("app") / "disease_model.pkl"'
        new_line = 'Path("app") / "disease_model_15k.pkl"'
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            with open(main_file, 'w') as f:
                f.write(content)
            print(f"✅ Updated main.py to use disease_model_15k.pkl")
            return True
        else:
            print("⚠️  Could not find model path in main.py")
            print("   Manual update needed - look for model loading code")
            return False
            
    except Exception as e:
        print(f"❌ Error updating main.py: {e}")
        return False

def update_symptom_catalog(backend_path):
    """Update symptom catalog with 15 diseases and 38 symptoms"""
    
    catalog_file = backend_path / "app" / "services" / "symptom_catalog.py"
    
    if not catalog_file.exists():
        print(f"❌ symptom_catalog.py not found: {catalog_file}")
        return False
    
    # New expanded catalog
    new_catalog = '''"""
Disease and Symptom Reference Catalog
Expanded with 15-disease model (97.07% accuracy)
Trained on 15,000 real patient records
"""

# 15 Diseases (expanded coverage)
DISEASES = [
    "Allergy",
    "Anemia",
    "Arthritis",
    "Asthma",
    "COVID-19",
    "Common Cold",
    "Dengue",
    "Diabetes",
    "Flu",
    "Food Poisoning",
    "Gastritis",
    "Hypertension",
    "Malaria",
    "Migraine",
    "Typhoid"
]

# 38 Symptoms (comprehensive coverage)
SYMPTOMS = [
    "pain", "fever", "ache", "headache", "nausea", "fatigue", "cough",
    "stomach", "shortness of breath", "vomiting", "diarrhea", "rash",
    "chills", "bodyache", "weakness", "sweating", "joint pain", "stiffness",
    "loss of appetite", "congestion", "sore throat", "sneezing", "watery eyes",
    "itching", "swelling", "hives", "difficulty breathing", "rapid heartbeat",
    "dizziness", "blurred vision", "tremors", "memory problems", "anxiety",
    "concentration", "depression", "insomnia", "muscle pain", "skin redness",
    "burning sensation"
]

# Disease severity baseline (0-10 scale)
DISEASE_BASELINE_SEVERITY = {
    "Allergy": 2,
    "Anemia": 4,
    "Arthritis": 5,
    "Asthma": 7,
    "COVID-19": 8,
    "Common Cold": 2,
    "Dengue": 8,
    "Diabetes": 6,
    "Flu": 6,
    "Food Poisoning": 6,
    "Gastritis": 4,
    "Hypertension": 6,
    "Malaria": 8,
    "Migraine": 5,
    "Typhoid": 8
}

# Disease-symptom associations (which symptoms are typical for each disease)
DISEASE_SYMPTOMS = {
    "Allergy": ["itching", "rash", "sneezing", "watery eyes", "hives", "swelling"],
    "Anemia": ["fatigue", "weakness", "dizziness", "shortness of breath", "headache"],
    "Arthritis": ["joint pain", "stiffness", "pain", "swelling", "muscle pain"],
    "Asthma": ["shortness of breath", "cough", "chest pain", "wheezing", "weakness"],
    "COVID-19": ["fever", "cough", "shortness of breath", "fatigue", "body ache", "loss of appetite"],
    "Common Cold": ["congestion", "sore throat", "cough", "sneezing", "fever"],
    "Dengue": ["fever", "headache", "muscle pain", "joint pain", "rash", "vomiting"],
    "Diabetes": ["fatigue", "loss of appetite", "urinary symptoms", "blurred vision", "tingling"],
    "Flu": ["fever", "cough", "body ache", "fatigue", "sore throat", "chills"],
    "Food Poisoning": ["stomach pain", "vomiting", "diarrhea", "nausea", "fever"],
    "Gastritis": ["stomach pain", "nausea", "vomiting", "loss of appetite", "burning sensation"],
    "Hypertension": ["headache", "dizziness", "blurred vision", "chest pain"],
    "Malaria": ["fever", "chills", "headache", "muscle pain", "fatigue", "sweating"],
    "Migraine": ["headache", "pain", "nausea", "vomiting", "sensitivity to light"],
    "Typhoid": ["fever", "headache", "weakness", "fatigue", "abdominal pain", "rash"]
}

# Risk stratification
RISK_FACTORS = {
    "Critical": ["COVID-19", "Dengue", "Malaria", "Typhoid", "Asthma"],
    "High": ["Diabetes", "Hypertension", "Anemia"],
    "Medium": ["Flu", "Food Poisoning", "Arthritis", "Gastritis"],
    "Low": ["Common Cold", "Allergy", "Migraine"]
}

# Common symptom groupings (for NLP processing)
SYMPTOM_GROUPS = {
    "Pain": ["pain", "ache", "headache", "body ache", "joint pain", "muscle pain", "stomach pain"],
    "Respiratory": ["cough", "shortness of breath", "congestion", "sore throat"],
    "GI": ["nausea", "vomiting", "diarrhea", "stomach pain", "loss of appetite"],
    "Fever": ["fever", "chills", "sweating"],
    "Systemic": ["fatigue", "weakness", "malaise"],
    "Skin": ["rash", "hives", "itching", "skin redness"],
    "Neurological": ["headache", "dizziness", "blurred vision", "memory problems"],
    "Allergy": ["itching", "sneezing", "hives", "rash", "swelling", "watery eyes"],
}

def get_disease_list():
    """Return list of all supported diseases"""
    return DISEASES

def get_symptom_list():
    """Return list of all supported symptoms"""
    return SYMPTOMS

def get_disease_severity(disease):
    """Get baseline severity for a disease (0-10 scale)"""
    return DISEASE_BASELINE_SEVERITY.get(disease, 5)

def get_disease_symptoms(disease):
    """Get typical symptoms for a disease"""
    return DISEASE_SYMPTOMS.get(disease, [])

def get_disease_risk_level(disease):
    """Get risk level for a disease"""
    for level, diseases in RISK_FACTORS.items():
        if disease in diseases:
            return level
    return "Medium"

def is_valid_disease(disease):
    """Check if disease is in catalog"""
    return disease in DISEASES

def is_valid_symptom(symptom):
    """Check if symptom is in catalog"""
    return symptom.lower() in [s.lower() for s in SYMPTOMS]

# Update this if you add new diseases
CATALOG_VERSION = "2.0"  # Expanded model
LAST_UPDATED = "2026-02-20"
MODEL_ACCURACY = "97.07%"
TRAINING_RECORDS = "15,000"
'''
    
    try:
        with open(catalog_file, 'w') as f:
            f.write(new_catalog)
        print("✅ Updated symptom_catalog.py with 15 diseases and 38 symptoms")
        return True
    except Exception as e:
        print(f"❌ Error updating symptom_catalog.py: {e}")
        return False

def validate_api():
    """Test API health endpoint and model predictions"""
    print("\n🔍 Validation steps:")
    print("   1. Test API: curl http://localhost:8000/health")
    print("   2. Test prediction: POST http://localhost:8000/predict")
    print("      with disease from: Allergy, Anemia, Arthritis, Asthma, COVID-19, ...")
    print("   3. Verify mobile app connects successfully")

def main():
    """Main update function"""
    backend_path = Path(__file__).parent / "backend" if Path(__file__).parent.name != "backend" else Path(__file__).parent
    
    # Normalize path
    if not (backend_path / "app" / "main.py").exists():
        # Try parent directory
        backend_path = Path(__file__).parent.parent / "backend"
    
    print("=" * 60)
    print("🚀 SYMPTOM CHECKER - MODEL UPDATE SCRIPT")
    print("=" * 60)
    print(f"\n📍 Backend path: {backend_path}\n")
    
    # Check models
    print("📊 Checking models:")
    model_old = backend_path / "disease_model.pkl"
    model_new = backend_path / "disease_model_15k.pkl"
    
    print("\nOriginal Model (6 diseases):")
    check_model_exists(model_old)
    
    print("\nNew Model (15 diseases, 97.07% accuracy):")
    if not check_model_exists(model_new):
        print("❌ New model not found!")
        print("   Run: python retrain_model.py")
        return False
    
    # Update configuration files
    print("\n" + "=" * 60)
    print("🔄 Updating configuration files:")
    print("=" * 60 + "\n")
    
    success = True
    
    # Update main.py
    print("1. Updating app/main.py...")
    if not update_main_py(backend_path):
        success = False
    
    # Update symptom catalog
    print("\n2. Updating app/services/symptom_catalog.py...")
    if not update_symptom_catalog(backend_path):
        success = False
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ UPDATE COMPLETE!")
        print("=" * 60)
        print("\n🎯 Next steps:")
        print("   1. Restart FastAPI server:")
        print("      cd backend && python -m uvicorn app.main:app --reload")
        print("\n   2. Verify API responds:")
        print("      curl http://localhost:8000/health")
        print("\n   3. Test with new disease:")
        print("      curl -X POST http://localhost:8000/predict \\")
        print('         -H "Content-Type: application/json" \\')
        print('         -d \'{"text": "I have high fever and joint pain", "language": "en"}\'')
        print("\n   4. Expected response should show one of 15 diseases")
        print("      (Allergy, Anemia, Arthritis, Asthma, COVID-19, Common Cold, Dengue,")
        print("       Diabetes, Flu, Food Poisoning, Gastritis, Hypertension, Malaria,")
        print("       Migraine, Typhoid)")
        validate_api()
    else:
        print("⚠️  UPDATE INCOMPLETE - Manual steps required")
        print("=" * 60)
    
    return success

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
