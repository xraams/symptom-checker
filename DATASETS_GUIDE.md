# Dataset Management Guide

## Overview

The Symptom Checker now includes a comprehensive dataset management system supporting multiple formats and languages. Datasets are organized in the `/backend/data/` directory.

## Dataset Files

### 1. `diseases_symptoms.csv`
**Purpose:** Disease-symptom mappings with weights

**Columns:**
- `disease`: Disease name (e.g., "Influenza")
- `symptom`: Symptom ID (e.g., "fever")
- `weight`: Importance score (0-1, where 1 is most important)
- `description`: Optional clinical notes

**Example:**
```csv
disease,symptom,weight,description
Influenza,fever,0.95,High fever often above 39°C
Influenza,cough,0.9,Severe dry cough
Influenza,body_pain,0.85,Muscle and joint pain
```

**Usage:**
```python
from app.services.dataset_loader import DatasetLoader
loader = DatasetLoader()
df = loader.load_disease_symptoms_csv()
print(df)
```

### 2. `training_data.csv`
**Purpose:** Patient records for model training

**Columns:**
- `patient_id`: Unique patient identifier
- `age`: Patient age
- `gender`: M/F
- `disease`: Diagnosis label
- Symptom columns: 0-1 float values indicating presence/severity
- `duration_days`: How long symptoms lasted
- `severity`: 1-3 scale

**Example:**
```csv
patient_id,age,gender,disease,fever,cough,sore_throat,...,severity
P001,28,M,Common Cold,0.5,0.8,0.7,...,1
P002,35,F,Influenza,0.95,0.9,0.7,...,3
```

**Usage:**
```python
loader = DatasetLoader()
df = loader.load_training_data_csv()
# Use for model retraining
print(f"Training records: {len(df)}")
```

### 3. `multilingual_symptoms.json`
**Purpose:** Symptom synonyms in multiple languages

**Structure:**
```json
{
  "multilingual_symptoms": {
    "fever": {
      "english": ["fever", "high temperature", "pyrexia"],
      "hindi": ["bukhar", "बुखार", "tez garmi"],
      "telugu": ["jwaram", "జ్వరం"],
      "spanish": ["fiebre", "temperatura elevada"]
    },
    ...
  }
}
```

**Usage:**
```python
loader = DatasetLoader()
multilingual = loader.load_multilingual_symptoms_json()
fever_variants = multilingual['multilingual_symptoms']['fever']
# Returns all fever synonyms across all languages
```

## Using the Dataset Loader

### Basic Operations

```python
from app.services.dataset_loader import DatasetLoader

# Initialize
loader = DatasetLoader("data")

# Load datasets
diseases_df = loader.load_disease_symptoms_csv()
training_df = loader.load_training_data_csv()
multilingual_dict = loader.load_multilingual_symptoms_json()

# Get statistics
stats = loader.get_statistics()
print(stats)
# Output:
# {
#   'disease_symptom_records': 24,
#   'unique_diseases': 6,
#   'unique_symptoms': 18,
#   'training_records': 20,
#   'multilingual_symptoms': 18,
#   'languages': ['english', 'hindi', 'spanish', 'telugu']
# }
```

### Add Disease-Symptom Mapping

```python
loader.add_disease_symptom_record(
    disease="Asthma",
    symptom="shortness_of_breath",
    weight=0.95,
    description="Severe dyspnea, wheezing"
)
```

### Add Training Record

```python
loader.add_training_record({
    'patient_id': 'P021',
    'age': 42,
    'gender': 'M',
    'disease': 'Asthma',
    'fever': 0.0,
    'cough': 0.8,
    'shortness_of_breath': 0.95,
    # ... other symptoms
    'duration_days': 14,
    'severity': 2
})
```

### Add Multilingual Variants

```python
loader.add_multilingual_variant(
    symptom_id="shortness_of_breath",
    language="portuguese",
    variants=["falta de ar", "dispneia", "dificuldade respiratoria"]
)
```

### Export Data

```python
# Export to CSV
loader.export_to_format('csv', output_dir='exports')

# Export to JSON
loader.export_to_format('json', output_dir='exports')

# Export to Excel
loader.export_to_format('xlsx', output_dir='exports')

# Export all formats
loader.export_to_format('all', output_dir='exports')
```

## Using the Management Script

The script `manage_datasets.py` provides CLI access to dataset operations:

### Show All Datasets
```bash
cd backend
python manage_datasets.py show
```

Output:
```
================================================================================
DATASET STATISTICS
================================================================================
disease_symptom_records..................... 24
unique_diseases............................. 6
unique_symptoms............................. 18
training_records............................ 20
multilingual_symptoms....................... 18
languages................................... ['english', 'hindi', 'spanish', 'telugu']

================================================================================
DISEASE-SYMPTOM MAPPINGS
================================================================================

Influenza:
  - fever: 0.95
  - cough: 0.9
  - body_pain: 0.85
...
```

### Add Disease-Symptom Mapping
```bash
python manage_datasets.py add-disease "Asthma" "shortness_of_breath" 0.95 "Severe dyspnea"
```

### Add Multilingual Variants
```bash
python manage_datasets.py add-language "fever" "french" '["fievre", "temperature elevee"]'
```

### Export Datasets
```bash
# CSV format
python manage_datasets.py export csv

# All formats
python manage_datasets.py export all
```

## Enhanced NLP Service

The `EnhancedBiomedicalNLPService` dynamically loads multilingual synonyms from datasets:

```python
from app.services.nlp_service_enhanced import EnhancedBiomedicalNLPService

# Initialize with datasets
nlp = EnhancedBiomedicalNLPService(data_dir="data")

# Extract symptoms
text = "I have fever and body ache"
symptoms = nlp.extract_symptoms(text)
# Returns: ['fever', 'body_pain']

# Get stats
stats = nlp.get_stats()
print(stats)
# {
#   'total_symptoms': 18,
#   'indexed_symptoms': 18,
#   'total_synonym_variants': 156,
#   'avg_variants_per_symptom': 8
# }

# Add new variants dynamically
nlp.add_symptom_variants("fever", ["high temp", "elevated temp"])

# Get all synonyms for a symptom
fever_synonyms = nlp.get_symptom_synonyms("fever")
```

## Directory Structure

```
backend/
├── data/
│   ├── diseases_symptoms.csv        # Disease-symptom mappings
│   ├── training_data.csv             # Patient records for training
│   └── multilingual_symptoms.json    # Symptom synonyms (all languages)
├── app/
│   └── services/
│       ├── symptom_catalog.py        # Static symptom catalog
│       ├── dataset_loader.py         # Dataset loading & management
│       ├── nlp_service.py            # Original NLP service
│       ├── nlp_service_enhanced.py   # Enhanced NLP with datasets
│       └── ...
├── manage_datasets.py                # CLI for dataset management
└── ...
```

## Adding Your Own Datasets

### Step 1: Prepare CSV Files

Create `backend/data/diseases_symptoms.csv`:
```csv
disease,symptom,weight,description
Your Disease,symptom1,0.8,Description
Your Disease,symptom2,0.9,Description
```

Create `backend/data/training_data.csv`:
```csv
patient_id,age,gender,disease,fever,cough,...,duration_days,severity
P001,35,M,Your Disease,0.7,0.8,...,7,2
```

### Step 2: Add Multilingual Variants

Update `backend/data/multilingual_symptoms.json`:
```json
{
  "multilingual_symptoms": {
    "symptom1": {
      "english": ["term1", "term2"],
      "your_language": ["term_native1", "term_native2"]
    }
  }
}
```

### Step 3: Use in Application

The enhanced NLP service automatically loads your datasets:
```python
nlp = EnhancedBiomedicalNLPService()
# Now uses your disease-symptom mappings
```

### Step 4: Retrain Model

```python
from app.train_model import train_model
from app.services.dataset_loader import DatasetLoader

loader = DatasetLoader()
training_df = loader.load_training_data_csv()

# Features and target from your training data
X = training_df[[col for col in training_df.columns if col not in ['patient_id', 'disease', 'duration_days', 'severity']]]
y = training_df['disease']

# Train
train_model(X, y, output_path='model.pkl')
```

## Best Practices

1. **Keep datasets updated:** Regularly add new patient records and disease-symptom mappings
2. **Multilingual coverage:** Add synonyms in commonly spoken languages in your target region
3. **Quality control:** Verify weights (0-1) sum to expected values per disease
4. **Backup data:** Export to Excel/JSON periodically for backup and analysis
5. **Version control:** Track CSV/JSON changes via Git (exclude large binary models)

## Supported Languages

Currently included:
- English
- Hindi (transliterated & native script)
- Telugu (transliterated & native script)
- Spanish (basic)

To add more:
```python
loader.add_multilingual_variant(
    symptom_id="fever",
    language="french",
    variants=["fievre", "temperature_elevee", "pyexie"]
)
```

## Troubleshooting

### Dataset not loading
- Check file path: should be in `backend/data/`
- Verify CSV format (must have required columns)
- Check JSON syntax in multilingual_symptoms.json

### Symptoms not extracting
- Verify symptom terms are in multilingual_symptoms.json
- Check case sensitivity (all patterns converted to lowercase)
- For non-ASCII terms, ensure UTF-8 encoding

### Model performance issues
- Ensure training_data.csv has sufficient records (20+ recommended)
- Verify disease labels match DISEASES catalog
- Check symptom feature columns exist

## Next Steps

- Integrate with [Kaggle medical datasets](https://www.kaggle.com/datasets)
- Add real clinical data (with proper privacy measures)
- Implement automated dataset validation
- Create data quality dashboard
- Set up periodic model retraining pipeline

---

For questions or contributions, please refer to the main README.md
