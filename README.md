# Symptom Checker (Mobile + AI Backend)

Full implementation of a multilingual symptom-based disease prediction system with:
- Biomedical NLP-style symptom extraction
- CatBoost-based disease classifier
- Integrated Gradients-style explainability
- Risk stratification (Low/Moderate/High/Critical)
- Personalized diet recommendation
- Flutter mobile app (English, Hindi, Telugu + voice input)

## Project Structure

- `backend/` FastAPI inference server
- `mobile/` Flutter application

## 1) Backend Setup (FastAPI)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Train model (optional; startup auto-trains if model missing):

```powershell
python train_model.py
```

Run API:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

- `GET http://localhost:8000/health`

Prediction endpoint:

- `POST http://localhost:8000/predict`

Sample payload:

```json
{
  "language": "te",
  "text": "I have fever and cough since 2 days",
  "symptom_intensity": {
    "fever": 0.8,
    "cough": 0.7
  }
}
```

## 2) Mobile Setup (Flutter)

```powershell
cd mobile
flutter pub get
flutter run
```

### Android Emulator Networking

- Base URL in app is `http://10.0.2.2:8000` (works for Android emulator).
- For physical device, replace with your machine LAN IP in `mobile/lib/services/api_service.dart`.

## 3) Features Implemented

1. **Multilingual Input**: EN/HI/TE UI + locale-aware speech-to-text.
2. **Symptom Extraction**: keyword + synonym matching across English/Hindi/Telugu terms.
3. **Disease Prediction**: CatBoost multiclass model with rule-based fallback.
4. **Explainability**: Integrated gradients-style symptom contribution scoring.
5. **Risk Layer**: confidence + symptom intensity + disease baseline severity.
6. **Diet Layer**: disease- and risk-aware nutrition guidance.

## 4) Notes

- This is a production-structured MVP implementation for research/demo use.
- For clinical deployment, integrate validated datasets, medical governance, and regulatory compliance.
