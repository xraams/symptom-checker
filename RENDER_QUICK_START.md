# 🚀 RENDER.COM LAUNCH - 5 STEP CHECKLIST

**Your Path to Production:** Render.com (Option C)  
**Time Required:** 20-30 minutes  
**Cost:** Free tier ($0) or $7+/month  

---

## ✅ STEP-BY-STEP CHECKLIST

### ✅ STEP 1: Create GitHub Account & Repository (5 min)

- [ ] Go to: https://github.com/signup
- [ ] Create account with email
- [ ] Verify email address
- [ ] Go to: https://github.com/new
- [ ] Create repository named: **symptom-checker**
- [ ] Make it: **PUBLIC**
- [ ] Click: "Create repository"

**Your new repository URL:** `https://github.com/YOUR_USERNAME/symptom-checker`

---

### ✅ STEP 2: Upload Code to GitHub (5 min)

In PowerShell:

```powershell
# Step 1: Clone your new repository
cd Desktop
git clone https://github.com/YOUR_USERNAME/symptom-checker.git
cd symptom-checker

# Step 2: Configure git
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Step 3: Copy your code into this folder
# Copy everything from: E:\X_RAAMS\VS Code\SYMPTOM CHECKER\backend\
# To: Desktop\symptom-checker\

# Step 4: Check if model file is there
dir disease_model_15k.pkl  # Should exist

# Step 5: Verify requirements.txt exists
dir requirements.txt  # Should exist

# Step 6: Push to GitHub
git add .
git commit -m "Initial commit: Symptom Checker API with CatBoost ML model"
git push -u origin main
```

**Verify:** Go to `https://github.com/YOUR_USERNAME/symptom-checker` - You should see your code there!

---

### ✅ STEP 3: Create render.yaml File (2 min)

In your project folder, create file: `render.yaml`

```yaml
services:
  - type: web
    name: symptom-checker-api
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.12
```

Then push to GitHub:
```powershell
git add render.yaml
git commit -m "Add Render deployment configuration"
git push origin main
```

---

### ✅ STEP 4: Deploy to Render.com (5 min)

1. **Go to:** https://render.com/
2. **Click:** "Sign up"
3. **Select:** "Sign up with GitHub" (easiest)
4. **Authorize** Render to access your GitHub
5. **In Render Dashboard:**
   - Click: "New +"
   - Select: "Web Service"
   - Connect your "symptom-checker" repository
   - Click: "Connect"

6. **Configure deployment:**
   ```
   Service Name:        symptom-checker-api
   Environment:         Python 3
   Build Command:       pip install -r requirements.txt
   Start Command:       uvicorn app.main:app --host 0.0.0.0 --port $PORT
   Plan:                Free
   ```

7. **Click:** "Create Web Service"
8. **Wait:** 2-3 minutes for deployment
9. **Watch:** Top right shows "Live" when ready
10. **Copy URL:** `https://symptom-checker-api-xxxxx.onrender.com`

---

### ✅ STEP 5: Update Mobile App & Test (5 min)

**Update API URL:**

Edit: `mobile/lib/services/api_service.dart`

Replace this:
```dart
static String get _defaultBaseUrl {
  if (kIsWeb) {
    return 'http://127.0.0.1:8001';
  }
  // ... rest of code
}
```

With this:
```dart
static String get _defaultBaseUrl {
  const String productionUrl = 'https://symptom-checker-api-xxxxx.onrender.com';
  
  if (kIsWeb) {
    return productionUrl;
  }
  switch (defaultTargetPlatform) {
    case TargetPlatform.android:
    case TargetPlatform.iOS:
      return productionUrl;
    default:
      return productionUrl;
  }
}
```

**Rebuild and test:**
```bash
cd mobile
flutter clean
flutter pub get
flutter run -d chrome
```

**Test prediction in the app - should work!** ✅

---

## 🎯 Verification Tests

### Test 1: Health Check
```powershell
$URL = "https://symptom-checker-api-xxxxx.onrender.com"
Invoke-WebRequest -UseBasicParsing "$URL/health"
# Should return: {"status":"ok"}
```

### Test 2: Prediction
```powershell
$body = @{
  text = "fever and cough"
  language = "en"
  symptom_intensity = @{fever = 0.8; cough = 0.7}
} | ConvertTo-Json -Depth 6

Invoke-WebRequest -UseBasicParsing `
  -Uri "$URL/predict" `
  -Method POST `
  -ContentType 'application/json' `
  -Body $body | Select-Object -ExpandProperty Content
# Should return disease prediction
```

### Test 3: Mobile App
- Open Flutter app in Chrome/Android/iOS
- Enter symptoms
- Get prediction from production API
- Should work instantly! ✅

---

## 📊 Monitor Your Deployment

**View logs:**
```
https://render.com/dashboard
→ Click "symptom-checker-api"
→ Go to "Logs" tab
→ See real-time activity
```

**View metrics:**
```
https://render.com/dashboard
→ Click "symptom-checker-api"
→ Go to "Metrics" tab
→ CPU, Memory, Requests/sec
```

---

## 💡 Important Notes

### Free Tier Behavior
- Auto-spins down after 15 minutes of inactivity
- First request after spin-down takes 5-10 seconds
- Fully functional, just slower first request

### Keep It Running
**Option A:** Upgrade to Starter ($7/month)
- Always running
- Better performance

**Option B:** Use uptime monitor (free)
- Go to: https://uptimerobot.com/
- Create monitor for your Render URL
- Keeps API warm every 5 minutes

---

## 🚀 Done! What You Have Now

✅ **Live Production API**
- URL: `https://symptom-checker-api-xxxxx.onrender.com`
- Automatic HTTPS
- Global availability
- Logs and metrics

✅ **Connected Mobile App**
- Uses production API
- Works on web, Android, iOS
- Real predictions

✅ **Deployment System**
- GitHub + Render integration
- Auto-redeploy on code push
- Easy version control

---

## 📋 Checklist to Complete Launch

- [ ] GitHub account created
- [ ] Repository created
- [ ] Code pushed to GitHub
- [ ] render.yaml created and pushed
- [ ] Render.com account created
- [ ] Deployment successful (status: "Live")
- [ ] Health check passing
- [ ] Prediction endpoint working
- [ ] Mobile app updated with production URL
- [ ] Mobile app rebuilt and tested
- [ ] Verified end-to-end works
- [ ] Bookmarked Render dashboard

---

## 🎉 LAUNCH COMPLETE!

Your Symptom Checker is now **LIVE** and accessible globally! 🚀

**What's next:**
1. Monitor performance daily
2. Collect user feedback
3. Plan improvements
4. Monthly retraining

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed guide.

---

**Ready to start?** Go to https://github.com/signup→ **NOW!** 🚀

