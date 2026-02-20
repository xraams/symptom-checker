# 🚀 PRODUCTION LAUNCH - QUICK START GUIDE

**Last Updated:** February 20, 2026  
**Status:** Ready for Deployment  
**Estimated Time to Launch:** 30-45 minutes  

---

## 📌 What's Ready

✅ **Backend API** - Built and tested on localhost  
✅ **Mobile App** - Connected to API (updated to port 8001)  
✅ **Docker Setup** - Dockerfile ready for deployment  
✅ **Production Monitoring** - Scripts ready to track performance  
✅ **Feedback Collection** - Endpoints ready for user feedback  
✅ **Documentation** - Complete guides for deployment and monitoring  

---

## 🎯 Quick Start (Copy & Paste Commands)

### Phase 1: Setup GCP (5 minutes)

```powershell
# Step 1: Install tools
choco install google-cloud-sdk docker-desktop

# Step 2: Authenticate
gcloud auth login
gcloud projects create symptom-checker --name="Symptom Checker API"
gcloud config set project symptom-checker

# Step 3: Enable services
gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com
gcloud config set run/region us-central1
```

### Phase 2: Build & Push (10 minutes)

```powershell
# Step 4: Navigate to backend
Set-Location "e:/X_RAAMS/VS Code/SYMPTOM CHECKER/backend"

# Step 5: Build Docker image
docker build -t symptom-checker-api:latest .

# Step 6: Test locally
docker run -p 8080:8080 symptom-checker-api:latest &
Start-Sleep -Seconds 3
Invoke-WebRequest -UseBasicParsing http://localhost:8080/health
# Stop the container (Ctrl+C in the terminal where it's running)

# Step 7: Push to Google Registry
gcloud auth configure-docker gcr.io
docker tag symptom-checker-api:latest gcr.io/symptom-checker/symptom-checker-api:latest
docker push gcr.io/symptom-checker/symptom-checker-api:latest
```

### Phase 3: Deploy to Cloud Run (5 minutes)

```powershell
# Step 8: Deploy
gcloud run deploy symptom-checker-api `
  --image=gcr.io/symptom-checker/symptom-checker-api:latest `
  --platform=managed `
  --region=us-central1 `
  --allow-unauthenticated `
  --memory=512Mi `
  --cpu=1 `
  --timeout=60 `
  --max-instances=20

# SAVE THE OUTPUT URL (looks like: https://symptom-checker-api-xxxxx.a.run.app)
```

### Phase 4: Verify & Update App (10 minutes)

```powershell
# Step 9: Test production API
$CLOUD_URL = "https://symptom-checker-api-xxxxx.a.run.app"  # Use your URL!
Invoke-WebRequest -UseBasicParsing "$CLOUD_URL/health"

# Expected output: {"status":"ok"}

# Step 10: Update mobile app
# Edit: mobile/lib/services/api_service.dart
# Change: const String productionUrl = '$CLOUD_URL';
# (Replace the xxxxx part with your actual Cloud Run URL)

# Step 11: Rebuild mobile app
Set-Location "e:/X_RAAMS/VS Code/SYMPTOM CHECKER/mobile"
flutter clean
flutter pub get
flutter build web   # or: flutter run -d chrome
```

### Phase 5: Set Up Monitoring (5 minutes)

```powershell
# Step 12: Enable logging
gcloud services enable logging.googleapis.com

# Step 13: View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50 --follow

# Step 14: Run monitoring
Set-Location "e:/X_RAAMS/VS Code/SYMPTOM CHECKER/backend"
pip install requests -q
python production_monitoring.py
```

---

## 📊 Status Dashboard

After deployment, you can check status with:

```powershell
# Health check
curl https://symptom-checker-api-xxxxx.a.run.app/health

# Feedback stats
curl https://symptom-checker-api-xxxxx.a.run.app/feedback/stats

# View logs
gcloud logging read --limit 100
```

---

## 📱 Update Mobile App

After getting your Cloud Run URL, update the `api_service.dart`:

```dart
static String get _defaultBaseUrl {
  const String productionUrl = 'https://symptom-checker-api-xxxxx.a.run.app';
  // ... rest of code
}
```

Then rebuild:
```bash
flutter clean && flutter pub get && flutter build web
```

---

## 🎯 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| **gcloud command not found** | Restart terminal after installing Google Cloud SDK |
| **Docker build fails** | Run: `docker system prune` to clear cache, then rebuild |
| **Port 8080 in use** | Stop other containers: `docker ps` then `docker stop [ID]` |
| **Cloud Run deployment slow** | It can take 2-3 minutes, check status with `gcloud run services list` |
| **API returns 404** | Make sure the Cloud Run URL is correct in mobile app |
| **Mobile app can't connect** | Check firewall, try from different WiFi, verify URL in app |

---

## 📈 Monitor Performance Daily

```powershell
# Morning check
gcloud logging read --limit 50

# Performance review
python backend/production_monitoring.py

# Error check
gcloud logging read "severity=ERROR OR severity=CRITICAL" --limit 10
```

---

## 💬 Collect User Feedback

Users can submit feedback through the app:

1. Make a prediction
2. Tap "Submit Feedback"
3. Tell us if we got it right
4. Describe symptoms
5. Suggest features

All feedback is automatically logged and visible via:

```powershell
curl https://symptom-checker-api-xxxxx.a.run.app/feedback/stats
```

---

## 🔄 Monthly Retraining

Every month:

```powershell
# 1. Download feedback
gcloud logging read --format=json > feedback_month1.json

# 2. Analyze accuracy
python analyze_feedback.py feedback_month1.json

# 3. Retrain model (using your dataset + feedback)
python retrain_model.py  # From earlier in the conversation

# 4. Test new model
python test_model_load.py

# 5. Deploy new model
docker build -t symptom-checker-api:v2 .
docker push gcr.io/symptom-checker/symptom-checker-api:v2
gcloud run deploy symptom-checker-api --image=gcr.io/symptom-checker/symptom-checker-api:v2
```

---

## 🎉 You're Ready!

Everything is prepared. You have:

✅ **Pre-built Docker image** - Ready to deploy  
✅ **GCP account** - Free tier covers your needs  
✅ **Monitoring setup** - Track everything  
✅ **Feedback system** - Collect user data  
✅ **Documentation** - Know what to do  

**Next Step:** Start with "Phase 1: Setup GCP" above!

---

## 📞 Where to Find Help

- **Deployment issues:** See [CLOUD_RUN_DEPLOYMENT.md](CLOUD_RUN_DEPLOYMENT.md)
- **Monitoring/Feedback:** See [PRODUCTION_DEPLOYMENT_COMPLETE.md](PRODUCTION_DEPLOYMENT_COMPLETE.md)
- **Mobile app setup:** See [MOBILE_APP_CONNECTION.md](MOBILE_APP_CONNECTION.md)
- **All options:** See [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)

---

## 🚀 Final Checklist Before Launch

- [ ] GCP project created
- [ ] Docker image builds locally
- [ ] Docker image tests locally
- [ ] Image pushed to GCP Registry
- [ ] Cloud Run deployment successful
- [ ] Health check returns `{"status":"ok"}`
- [ ] Prediction endpoint works
- [ ] Mobile app URL updated
- [ ] Mobile app connects successfully
- [ ] Feedback endpoints accessible
- [ ] Monitoring shows metrics
- [ ] Team aware of deployment
- [ ] Documentation reviewed
- [ ] Backup plan documented

---

**Ready? Start with the Quick Start commands above!** 🚀

Once deployed, you'll have a production system that:
- Serves predictions globally via HTTPS
- Scales automatically with demand
- Collects user feedback for improvement
- Monitors performance 24/7
- Stays within free tier costs

**Estimated cost:** $0 per month (with free tier)

Good luck! 🎉

