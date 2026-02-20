#!/usr/bin/env python3
"""Test the retrained model predictions via the API"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001"

test_cases = [
    {
        "name": "COVID-19",
        "text": "high fever cough shortness of breath fatigue"
    },
    {
        "name": "Dengue",
        "text": "high fever with joint pain and rash headache"
    },
    {
        "name": "Malaria",
        "text": "fever with chills body ache and sweating"
    },
    {
        "name": "Asthma",
        "text": "shortness of breath difficulty breathing wheezing"
    },
    {
        "name": "Allergy",
        "text": "itching rash sneezing watery eyes and hives"
    },
    {
        "name": "Diabetes",
        "text": "fatigue blurred vision loss of appetite weakness"
    },
    {
        "name": "Typhoid",
        "text": "prolonged fever headache weakness and rash"
    },
    {
        "name": "Hypertension",
        "text": "headache dizziness blurred vision chest pain"
    },
]

print("🧪 Testing Retrained Model Predictions")
print("=" * 70)
print()

for case in test_cases:
    payload = {
        "text": case["text"],
        "language": "en",
        "symptom_intensity": {}
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            pred = data.get("predicted_disease", "N/A")
            conf = data.get("confidence", 0)
            risk = data.get("risk_level", "N/A")
            
            print(f"📋 Test: {case['name']}")
            print(f"   Input: '{case['text']}'")
            print(f"   ✓ Predicted: {pred}")
            print(f"   ✓ Confidence: {conf*100:.1f}%")
            print(f"   ✓ Risk Level: {risk}")
        else:
            print(f"✗ Error ({response.status_code}): {response.text}")
    
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()

print("=" * 70)
print("✅ Testing complete!")
