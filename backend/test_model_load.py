#!/usr/bin/env python3
"""Quick test to verify the retrained model loads correctly"""

import pickle
from pathlib import Path

model_path = Path(__file__).parent / "disease_model_15k.pkl"
print(f'Loading model from: {model_path}')
print(f'File exists: {model_path.exists()}')
print(f'File size: {model_path.stat().st_size / 1024 / 1024:.2f} MB')

try:
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    
    print(f'\n✓ Model loaded successfully')
    print(f'  Keys: {list(model_data.keys())}')
    
    diseases = list(model_data['label_encoder'].classes_)
    print(f'  Diseases: {len(diseases)} classes')
    print(f'  Classes: {diseases}')
    
    print(f'\n✓ Model is ready to use!')
    print(f'  Supports {len(diseases)} diseases')
    
except Exception as e:
    print(f'\n✗ Error loading model: {e}')
    import traceback
    traceback.print_exc()
