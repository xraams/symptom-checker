"""
Disease and Symptom Reference Catalog
Expanded with 15-disease model (97.07% test accuracy)
Trained on 15,000 real patient records
"""

# 15 Diseases with expanded coverage
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
    "Typhoid",
]

# 38 Symptoms extracted from 15,000 patient records
SYMPTOMS = [
    "pain",
    "fever",
    "ache",
    "headache",
    "nausea",
    "fatigue",
    "cough",
    "stomach",
    "shortness_of_breath",
    "vomiting",
    "diarrhea",
    "rash",
    "chills",
    "bodyache",
    "weakness",
    "sweating",
    "joint_pain",
    "stiffness",
    "loss_of_appetite",
    "congestion",
    "sore_throat",
    "sneezing",
    "watery_eyes",
    "itching",
    "swelling",
    "hives",
    "difficulty_breathing",
    "rapid_heartbeat",
    "dizziness",
    "blurred_vision",
    "tremors",
    "memory_problems",
    "anxiety",
    "concentration",
    "depression",
    "insomnia",
    "muscle_pain",
    "skin_redness",
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
    "Typhoid": 8,
}

# Disease-symptom associations (typical symptoms for each disease)
DISEASE_SYMPTOMS = {
    "Allergy": ["itching", "rash", "sneezing", "watery_eyes", "hives", "swelling", "congestion"],
    "Anemia": ["fatigue", "weakness", "dizziness", "shortness_of_breath", "headache"],
    "Arthritis": ["joint_pain", "stiffness", "pain", "swelling", "muscle_pain"],
    "Asthma": ["shortness_of_breath", "cough", "chest_pain", "wheezing", "weakness"],
    "COVID-19": ["fever", "cough", "shortness_of_breath", "fatigue", "bodyache", "loss_of_appetite"],
    "Common Cold": ["congestion", "sore_throat", "cough", "sneezing", "fever", "fatigue"],
    "Dengue": ["fever", "headache", "muscle_pain", "joint_pain", "rash", "vomiting"],
    "Diabetes": ["fatigue", "loss_of_appetite", "blurred_vision", "urinary_issues", "neuropathy"],
    "Flu": ["fever", "cough", "bodyache", "fatigue", "sore_throat", "chills"],
    "Food Poisoning": ["stomach", "vomiting", "diarrhea", "nausea", "fever"],
    "Gastritis": ["stomach", "nausea", "vomiting", "loss_of_appetite"],
    "Hypertension": ["headache", "dizziness", "blurred_vision", "chest_pain"],
    "Malaria": ["fever", "chills", "headache", "muscle_pain", "fatigue", "sweating"],
    "Migraine": ["headache", "pain", "nausea", "vomiting"],
    "Typhoid": ["fever", "headache", "weakness", "fatigue", "stomach", "rash"],
}

# Risk stratification
RISK_FACTORS = {
    "Critical": ["COVID-19", "Dengue", "Malaria", "Typhoid", "Asthma"],
    "High": ["Diabetes", "Hypertension", "Anemia"],
    "Medium": ["Flu", "Food Poisoning", "Arthritis", "Gastritis"],
    "Low": ["Common Cold", "Allergy", "Migraine"],
}

# Multilingual symptom mappings
SYMPTOM_SYNONYMS = {
    "fever": ["fever", "high temperature", "pyrexia", "bukhar", "बुखार", "జ్వరం", "તાપમાન"],
    "cough": ["cough", "khansi", "खांसी", "దగ్గు", "ખાંસી"],
    "sore_throat": ["sore throat", "throat pain", "gala dard", "गले में दर्द", "గొంతు నొప్పి", "ગળાની પીડા"],
    "congestion": ["congestion", "stuffed nose", "nasal block"],
    "headache": ["headache", "sar dard", "सर दर्द", "తలనొప్పి", "માથાનો દર્દ"],
    "fatigue": ["fatigue", "tired", "weakness", "thakaan", "थकान", "అలసట"],
    "nausea": ["nausea", "uneasy stomach", "मतली", "వికారం", "ગુમટી"],
    "vomiting": ["vomit", "vomiting", "ulti", "उल्टी", "వాంతులు"],
    "diarrhea": ["diarrhea", "loose motion", "dast", "दस्त", "విసర్జన"],
    "stomach": ["stomach pain", "abdominal pain", "pet dard", "पेट दर्द", "కడుపు నొప్పి"],
    "shortness_of_breath": ["breathless", "shortness of breath", "saans", "सांस लेने में तकलीफ"],
    "bodyache": ["body pain", "muscle pain", "body ache"],
    "joint_pain": ["joint pain", "bone pain"],
    "weakness": ["weakness", "tired", "exhausted"],
    "pain": ["pain", "ache", "दर्द", "నొప్పి"],
    "ache": ["ache", "pain", "दर्द"],
    "rash": ["rash", "skin rash", "खुजली"],
    "chills": ["chills", "shivering", "कंपकंपी"],
    "sweating": ["sweating", "perspiration"],
    "stiffness": ["stiffness", "rigidity"],
    "loss_of_appetite": ["no appetite", "lack of appetite"],
    "sneezing": ["sneezing", "achoo", "छींक"],
    "watery_eyes": ["watery eyes", "tears"],
    "itching": ["itching", "itch", "खुजली"],
    "swelling": ["swelling", "edema", "सूजन"],
    "hives": ["hives", "urticaria", "पित्ती"],
    "difficulty_breathing": ["difficulty breathing", "breathing problems"],
    "dizziness": ["dizziness", "vertigo", "चक्कर"],
    "blurred_vision": ["blurred vision", "vision problems"],
    "tremors": ["tremors", "shaking"],
    "memory_problems": ["memory loss", "forgetfulness"],
    "anxiety": ["anxiety", "nervousness"],
    "depression": ["depression", "sadness"],
    "insomnia": ["insomnia", "sleeplessness"],
    "muscle_pain": ["muscle pain", "myalgia"],
    "skin_redness": ["redness", "erythema"],
}

# Common symptom groupings (for NLP processing)
SYMPTOM_GROUPS = {
    "Pain": ["pain", "ache", "headache", "bodyache", "joint_pain", "muscle_pain", "stomach"],
    "Respiratory": ["cough", "shortness_of_breath", "congestion", "sore_throat", "difficulty_breathing"],
    "GI": ["nausea", "vomiting", "diarrhea", "stomach", "loss_of_appetite"],
    "Fever": ["fever", "chills", "sweating"],
    "Systemic": ["fatigue", "weakness"],
    "Skin": ["rash", "hives", "itching", "skin_redness", "swelling"],
    "Neurological": ["headache", "dizziness", "blurred_vision", "memory_problems", "tremors"],
    "Allergy": ["itching", "sneezing", "hives", "rash", "swelling", "watery_eyes", "congestion"],
    "Cardiac": ["rapid_heartbeat", "chest_pain", "shortness_of_breath", "dizziness"],
    "Mental": ["anxiety", "depression", "insomnia", "memory_problems"],
}

# Update this if you add new diseases
CATALOG_VERSION = "2.0"  # Expanded with 15 diseases
LAST_UPDATED = "2026-02-20"
MODEL_ACCURACY = "97.07%"
TRAINING_RECORDS = "15,000"


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


def get_symptom_variants(symptom):
    """Get all variants (multilingual) of a symptom"""
    return SYMPTOM_SYNONYMS.get(symptom, [symptom])

