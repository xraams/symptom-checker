# 📱 MOBILE APP CONNECTION GUIDE

## Quick Setup (2 minutes)

Your Flutter mobile app is already compatible with the new API. Just update one file!

### Step 1: Update API Base URL

Open: **`mobile/lib/app/config/environment.dart`**

Find this line:
```dart
// OLD
static const String apiBaseUrl = 'http://localhost:8000';
```

Replace with:
```dart
// NEW
static const String apiBaseUrl = 'http://127.0.0.1:8001';
```

### Step 2: Rebuild Mobile App

```bash
cd mobile
flutter clean
flutter pub get
flutter run -d chrome  # or -d windows/android/ios
```

That's it! Your app now connects to the new 15-disease model.

---

## API Integration Details

### Available Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check API status |
| `/predict` | POST | Get disease prediction |

### Request Format

```json
POST /predict
{
  "text": "symptoms description",
  "language": "en",
  "symptom_intensity": {}
}
```

### Response Format

```json
{
  "predicted_disease": "COVID-19",
  "confidence": 0.823,
  "top_k": [
    {"COVID-19": 0.823},
    {"Flu": 0.124},
    {"Common Cold": 0.053}
  ],
  "risk_level": "Critical",
  "risk_score": 8.5,
  "detected_symptoms": ["fever", "cough"],
  "explainability": [
    {
      "symptom": "fever",
      "importance": 0.45,
      "contribution": "positive"
    }
  ],
  "diet": {
    "foods_to_eat": ["..."],
    "foods_to_avoid": ["..."],
    "hydration": "high"
  }
}
```

---

## Supported Diseases (15 Total)

The API now supports these 15 diseases:

1. **Allergy** - Common allergic reactions
2. **Anemia** - Low red blood cell count
3. **Arthritis** - Joint inflammation
4. **Asthma** - Respiratory condition (Critical)
5. **COVID-19** - Coronavirus disease (Critical)
6. **Common Cold** - Viral infection
7. **Dengue** - Mosquito-borne fever (Critical)
8. **Diabetes** - Metabolic disorder
9. **Flu** - Influenza
10. **Food Poisoning** - Foodborne illness
11. **Gastritis** - Stomach inflammation
12. **Hypertension** - High blood pressure
13. **Malaria** - Parasitic infection (Critical)
14. **Migraine** - Severe headache
15. **Typhoid** - Bacterial infection (Critical)

---

## Example Implementation (Dart/Flutter)

### Basic Usage

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class APIService {
  static const String baseUrl = 'http://127.0.0.1:8001';
  
  static Future<Map<String, dynamic>> predict({
    required String symptoms,
    String language = 'en',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/predict'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'text': symptoms,
          'language': language,
          'symptom_intensity': {},
        }),
      ).timeout(Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('API Error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to get prediction: $e');
    }
  }
  
  static Future<bool> healthCheck() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
      ).timeout(Duration(seconds: 5));
      
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}

// Usage in your widget
class PredictScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map<String, dynamic>>(
      future: APIService.predict(
        symptoms: 'fever and cough',
        language: 'en',
      ),
      builder: (context, snapshot) {
        if (snapshot.hasData) {
          final disease = snapshot.data!['predicted_disease'];
          final confidence = snapshot.data!['confidence'];
          
          return Text('Predicted: $disease ($confidence%)');
        }
        return CircularProgressIndicator();
      },
    );
  }
}
```

---

## Network Setup

### Local Development

```bash
# API running on your PC
POST http://127.0.0.1:8001/predict

# From Flutter
- Web: http://127.0.0.1:8001
- Android Emulator: http://10.0.2.2:8001
- Android Device: http://<YOUR_PC_IP>:8001
- iOS Simulator: http://127.0.0.1:8001
- iOS Device: http://<YOUR_PC_IP>:8001
- Windows: http://127.0.0.1:8001
```

### Production Deployment

Once deployed to cloud:

```dart
static const String apiBaseUrl = 'https://api.yourdomain.com';
```

---

## Troubleshooting

### "Connection refused" Error

✓ **Solution:** Make sure API is running
```bash
# Check if API is responding
curl http://127.0.0.1:8001/health
# Should return: {"status":"ok"}
```

### Timeout Error

✓ **Solution:** Increase timeout in your HTTP client
```dart
.timeout(Duration(seconds: 30))  // Increase from 10 to 30
```

### CORS Error (Browser)

✓ **Solution:** API already has CORS enabled
- Check that your request headers are correct
- Verify Content-Type is 'application/json'

### Low Prediction Accuracy

✓ **Solution:** Provide more detailed symptoms
- Instead of: "fever"
- Try: "high fever with cough and fatigue"

---

## Performance Tips

1. **Cache Results** - Cache recent predictions to reduce API calls
2. **Batch Requests** - Group multiple predictions in one request
3. **Monitor Latency** - Track response times (target: <100ms)
4. **Use Health Checks** - Call `/health` before making predictions
5. **Error Handling** - Implement retry logic for failed requests

---

## Next Steps

1. ✅ Update API URL in your app code
2. ✅ Rebuild and test locally
3. ✅ Test with different symptoms
4. ✅ Verify all 15 diseases are recognized
5. ✅ Monitor performance using `monitor_api.py`
6. ✅ When ready, deploy API to cloud server

---

## Support

For issues with API integration:
- Check mobile app logs: `flutter logs`
- Test API directly: `curl http://127.0.0.1:8001/predict`
- Review monitoring results: `monitoring_results.json`
- Check `DEPLOYMENT_REFERENCE.md` for troubleshooting

