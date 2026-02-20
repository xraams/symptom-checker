"""
API Monitoring & Analytics Script
Track prediction accuracy, response times, and system performance
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List
from collections import defaultdict

class APIMonitor:
    """Monitor Symptom Checker API performance"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:8001"):
        self.api_url = api_url
        self.predictions = []
        self.response_times = []
        self.accuracy_by_disease = defaultdict(lambda: {"correct": 0, "total": 0})
    
    def test_prediction(self, text: str, expected_disease: str = None) -> Dict:
        """Make a prediction and track metrics"""
        payload = {
            "text": text,
            "language": "en",
            "symptom_intensity": {}
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.api_url}/predict",
                json=payload,
                timeout=5
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "input": text,
                    "predicted_disease": data.get("predicted_disease"),
                    "confidence": data.get("confidence"),
                    "risk_level": data.get("risk_level"),
                    "response_time_ms": response_time * 1000,
                    "detected_symptoms": data.get("detected_symptoms"),
                    "status": "success"
                }
                
                # Track accuracy if we have expected disease
                if expected_disease:
                    is_correct = data.get("predicted_disease") == expected_disease
                    result["correct"] = is_correct
                    self.accuracy_by_disease[expected_disease]["total"] += 1
                    if is_correct:
                        self.accuracy_by_disease[expected_disease]["correct"] += 1
                
                self.predictions.append(result)
                self.response_times.append(response_time * 1000)
                
                return result
            else:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "status": "error",
                    "error": f"HTTP {response.status_code}",
                    "response_time_ms": response_time * 1000
                }
        
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }
    
    def print_stats(self):
        """Print performance statistics"""
        if not self.predictions:
            print("No predictions recorded yet")
            return
        
        print("\n" + "=" * 70)
        print("📊 API PERFORMANCE STATISTICS")
        print("=" * 70)
        
        # Response time stats
        avg_response_time = sum(self.response_times) / len(self.response_times)
        min_response_time = min(self.response_times)
        max_response_time = max(self.response_times)
        
        print(f"\n⏱️  Response Times:")
        print(f"   Average: {avg_response_time:.2f}ms")
        print(f"   Min: {min_response_time:.2f}ms")
        print(f"   Max: {max_response_time:.2f}ms")
        
        # Success rate
        successful = [p for p in self.predictions if p.get("status") == "success"]
        success_rate = len(successful) / len(self.predictions) * 100
        print(f"\n✓ Success Rate: {success_rate:.1f}% ({len(successful)}/{len(self.predictions)})")
        
        # Accuracy by disease
        if self.accuracy_by_disease:
            print(f"\n🏥 Accuracy by Disease:")
            for disease, stats in sorted(self.accuracy_by_disease.items()):
                if stats["total"] > 0:
                    accuracy = stats["correct"] / stats["total"] * 100
                    print(f"   {disease}: {accuracy:.1f}% ({stats['correct']}/{stats['total']})")
        
        # Confidence stats
        confidences = [p.get("confidence", 0) for p in successful]
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            print(f"\n📈 Average Confidence: {avg_confidence:.2%}")
        
        print("\n" + "=" * 70)

# Example usage
if __name__ == "__main__":
    monitor = APIMonitor()
    
    print("🧪 Running API Monitoring Tests")
    print("=" * 70)
    
    test_cases = [
        ("fever cough shortness of breath", "COVID-19"),
        ("high fever joint pain rash headache", "Dengue"),
        ("fever chills body ache sweating", "Malaria"),
        ("shortness of breath difficulty breathing", "Asthma"),
        ("itching rash sneezing watery eyes", "Allergy"),
        ("fatigue blurred vision loss of appetite", "Diabetes"),
        ("fever weakness headache prolonged", "Typhoid"),
        ("headache dizziness blurred vision", "Hypertension"),
    ]
    
    for text, expected in test_cases:
        result = monitor.test_prediction(text, expected)
        status = "✓" if result.get("status") == "success" else "✗"
        print(f"{status} {result.get('predicted_disease', 'ERROR')}: {result.get('response_time_ms', 0):.1f}ms")
    
    monitor.print_stats()
    
    # Save results to file
    with open("monitoring_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "predictions": monitor.predictions,
            "accuracy_by_disease": {k: dict(v) for k, v in monitor.accuracy_by_disease.items()}
        }, f, indent=2)
    
    print("\n✓ Results saved to monitoring_results.json")
