# 🚀 GCP CLOUD RUN DEPLOYMENT GUIDE

**Platform:** Google Cloud Run (Free Tier)  
**Cost:** $0 for first 2 million requests/month  
**Deployment Time:** ~15 minutes  

---

## Step 1: Prerequisites

You'll need:
- Google Account (free)
- Gcloud CLI installed
- Docker installed
- Git for version control

### Install Google Cloud SDK

```powershell
# Download and install from:
# https://cloud.google.com/sdk/docs/install

# Or use Chocolatey:
choco install google-cloud-sdk

# Verify installation:
gcloud --version
```

### Install Docker

```powershell
# Download from: https://www.docker.com/products/docker-desktop
# Or use Chocolatey:
choco install docker-desktop

# Verify installation:
docker --version
```

---

## Step 2: Create GCP Project

```powershell
# Login to Google Cloud
gcloud auth login

# Create a new project
gcloud projects create symptom-checker --name="Symptom Checker API"

# Set the project as active
gcloud config set project symptom-checker

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Set your region (us-central1 is free tier eligible)
gcloud config set run/region us-central1
```

---

## Step 3: Create Dockerfile for Backend

Create file: `backend/Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Cloud Run sets PORT env var)
ENV PORT=8080

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## Step 4: Update Backend for Cloud Deployment

Update `backend/app/main.py`:

```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Symptom Checker API")

# Configure CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8001",
        os.getenv("ALLOWED_ORIGINS", "").split(","),  # Add production domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... rest of routes ...
```

---

## Step 5: Build and Test Docker Image Locally

```powershell
# Navigate to backend directory
Set-Location "e:/X_RAAMS/VS Code/SYMPTOM CHECKER/backend"

# Build the Docker image
docker build -t symptom-checker-api:latest .

# Test locally
docker run -p 8080:8080 symptom-checker-api:latest

# In another terminal, test:
Invoke-WebRequest -UseBasicParsing http://localhost:8080/health
```

---

## Step 6: Push to Google Container Registry

```powershell
# Configure Docker to use gcloud as credential helper
gcloud auth configure-docker

# Tag image for GCP
docker tag symptom-checker-api:latest gcr.io/symptom-checker/symptom-checker-api:latest

# Push to Container Registry
docker push gcr.io/symptom-checker/symptom-checker-api:latest

# Verify push:
gcloud container images list
```

---

## Step 7: Deploy to Cloud Run

```powershell
# Deploy the image
gcloud run deploy symptom-checker-api `
  --image=gcr.io/symptom-checker/symptom-checker-api:latest `
  --platform=managed `
  --region=us-central1 `
  --allow-unauthenticated `
  --memory=512Mi `
  --cpu=1 `
  --timeout=60 `
  --max-instances=20

# The command will output your service URL like:
# https://symptom-checker-api-xxxxx.a.run.app
```

---

## Step 8: Verify Production Deployment

```powershell
# Copy the service URL from the output above
$PROD_URL = "https://symptom-checker-api-xxxxx.a.run.app"

# Health check
Invoke-WebRequest -UseBasicParsing "$PROD_URL/health" | Select-Object -ExpandProperty Content

# Test prediction
$body = @{
  text = "fever and cough"
  language = "en"
  symptom_intensity = @{
    fever = 0.8
    cough = 0.7
  }
} | ConvertTo-Json -Depth 6

Invoke-WebRequest -UseBasicParsing `
  -Uri "$PROD_URL/predict" `
  -Method POST `
  -ContentType 'application/json' `
  -Body $body | Select-Object -ExpandProperty Content
```

---

## Step 9: Update Mobile App for Production

Edit: `mobile/lib/services/api_service.dart`

```dart
class ApiService {
  ApiService({String? baseUrl})
  : _dio = Dio(BaseOptions(baseUrl: baseUrl ?? _defaultBaseUrl));

  static String get _defaultBaseUrl {
    // Use production URL
    const String productionUrl = 'https://symptom-checker-api-xxxxx.a.run.app';
    
    if (kIsWeb) {
      return productionUrl;
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
      case TargetPlatform.iOS:
        return productionUrl;
      default:
        return productionUrl;  // Windows, Linux, macOS
    }
  }
  
  // ... rest of code ...
}
```

---

## Step 10: Rebuild and Deploy Mobile App

```bash
cd mobile

# Clean and get dependencies
flutter clean
flutter pub get

# Build for web
flutter build web

# Build for Android
flutter build apk --release

# Build for iOS
flutter build ios --release
```

---

## Step 11: Set Up Monitoring

### Enable Cloud Logging

```powershell
gcloud services enable logging.googleapis.com

# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=symptom-checker-api" --limit 50 --format json
```

### Enable Cloud Monitoring

```powershell
gcloud services enable monitoring.googleapis.com
gcloud services enable cloudtrace.googleapis.com
```

---

## Step 12: Configure Auto-Scaling

```powershell
# Update Cloud Run service with auto-scaling
gcloud run services update symptom-checker-api `
  --max-instances=50 `
  --min-instances=1 `
  --concurrency=80 `
  --memory=512Mi `
  --timeout=60 `
  --region=us-central1
```

---

## Step 13: Set Up Custom Domain (Optional)

```powershell
# Add custom domain to Cloud Run
gcloud run domain-mappings create `
  --service=symptom-checker-api `
  --domain=symptom-api.yourdomain.com `
  --region=us-central1

# Follow the prompts to add DNS records
```

---

## Monitoring Setup

### 1. View Real-time Logs

```powershell
# Stream logs from Cloud Run
gcloud logging read "resource.type=cloud_run_revision" --limit 100 --follow
```

### 2. Create Alert Policy

```powershell
# Alert when error rate > 5%
gcloud alpha monitoring policies create `
  --notification-channels=YOUR_CHANNEL_ID `
  --alert-strategy='{"autoClose":"1800s"}' `
  --display-name="High Error Rate" `
  --condition-threshold-value=0.05
```

### 3. Monitor Costs

The free tier includes:
- 2 million requests/month
- 360,000 GB-seconds/month CPU
- 90,000 GB-months memory storage

Cost estimator: https://cloud.google.com/run/pricing

---

## Cost Summary (Free Tier)

| Resource | Free Tier | Cost When Exceeded |
|----------|-----------|-------------------|
| Requests | 2M/month | $0.40 per 1M |
| GB-seconds (CPU) | 360,000/month | $0.00002500 per GB-second |
| GB-months (Memory) | 90,000/month | $0.0000050 per GB-month |

**Estimated cost for 10,000 users/month:** $0 - $20

---

## Troubleshooting

### Service fails to build
```powershell
# Check Cloud Build logs
gcloud builds log [BUILD_ID] --stream
```

### Service timeout on deploy
```powershell
# Increase timeout
gcloud run services update symptom-checker-api `
  --timeout=600 `
  --region=us-central1
```

### CORS errors from mobile app
```powershell
# Verify CORS is configured in main.py
# Add your domain to allow_origins
```

### High latency (>1s)
```powershell
# Check if Cold Start is happening
# Increase min-instances (costs ~$10-15/month per instance)
gcloud run services update symptom-checker-api `
  --min-instances=2
```

---

## Post-Deployment Checklist

- [ ] Health check passes
- [ ] Predictions working
- [ ] Mobile app connects and receives predictions
- [ ] Logs are being collected
- [ ] Monitoring alerts configured
- [ ] Custom domain configured (if needed)
- [ ] SSL/HTTPS working (automatic with Cloud Run)
- [ ] Performance baseline established
- [ ] Backup strategy documented
- [ ] Team trained on monitoring

---

## Next Steps

1. **Test thoroughly** - Run 24-hour stability test
2. **Gather metrics** - Monitor performance daily
3. **User feedback** - Collect predictions and accuracy
4. **Retraining** - Monthly model updates with new data
5. **Scaling** - Increase resources as needed

---

## Useful Commands Reference

```powershell
# View all deployments
gcloud run services list

# View service details
gcloud run services describe symptom-checker-api --region us-central1

# Update service
gcloud run services update symptom-checker-api --region us-central1 [OPTIONS]

# View recent revisions
gcloud run revisions list --service symptom-checker-api --region us-central1

# Rollback to previous version
gcloud run services update-traffic symptom-checker-api --to-revisions [REVISION_ID]=100 --region us-central1

# Delete service
gcloud run services delete symptom-checker-api --region us-central1

# View Cloud Logs
gcloud logging read --limit 50 --format json

# Monitor service metrics
gcloud monitoring dashboards create --config-from-file=dashboard.json
```

---

## Success Indicators

✅ **Deployment Successful When:**
- Service URL accessible from anywhere
- Health check returns `{"status":"ok"}`
- API responds in <500ms from anywhere
- All disease predictions working
- Mobile app connects and receives results
- Logs visible in Cloud Logging
- Monitoring dashboard showing metrics

**Estimated time for this deployment:** 15-20 minutes

