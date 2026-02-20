"""
Production Monitoring & Feedback Collection System
Tracks API performance, user feedback, and model accuracy in production
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
import requests


class ProductionMonitor:
    """Monitor production API performance and health"""
    
    def __init__(self, api_url: str, log_file: str = "production_metrics.json"):
        self.api_url = api_url
        self.log_file = log_file
        self.metrics = {
            "timestamp": datetime.now().isoformat(),
            "predictions": [],
            "health_checks": [],
            "errors": [],
            "summary": {}
        }
    
    def health_check(self) -> Dict:
        """Check API health"""
        try:
            start = time.time()
            response = requests.get(f"{self.api_url}/health", timeout=10)
            response_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "status": "healthy",
                    "response_time_ms": response_time,
                    "endpoint": "/health"
                }
                self.metrics["health_checks"].append(result)
                return result
            else:
                self._log_error(f"Health check failed: {response.status_code}")
                return {"status": "unhealthy", "code": response.status_code}
        except Exception as e:
            self._log_error(f"Health check error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def test_prediction(self, text: str, language: str = "en") -> Dict:
        """Test prediction endpoint"""
        try:
            start = time.time()
            payload = {
                "text": text,
                "language": language,
                "symptom_intensity": {}
            }
            response = requests.post(
                f"{self.api_url}/predict",
                json=payload,
                timeout=10
            )
            response_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "input": text,
                    "predicted_disease": data.get("predicted_disease"),
                    "confidence": data.get("confidence"),
                    "response_time_ms": response_time,
                    "status": "success"
                }
                self.metrics["predictions"].append(result)
                return result
            else:
                self._log_error(f"Prediction failed: {response.status_code}")
                return {"status": "failed", "code": response.status_code}
        except Exception as e:
            self._log_error(f"Prediction error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _log_error(self, error_msg: str):
        """Log errors"""
        self.metrics["errors"].append({
            "timestamp": datetime.now().isoformat(),
            "error": error_msg
        })
    
    def calculate_summary(self):
        """Calculate performance summary"""
        predictions = self.metrics["predictions"]
        if not predictions:
            return
        
        response_times = [p["response_time_ms"] for p in predictions if "response_time_ms" in p]
        
        self.metrics["summary"] = {
            "total_predictions": len(predictions),
            "success_rate": f"{(sum(1 for p in predictions if p['status'] == 'success') / len(predictions) * 100):.1f}%",
            "avg_response_time_ms": round(sum(response_times) / len(response_times), 2) if response_times else 0,
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "total_errors": len(self.metrics["errors"]),
            "health_checks_passed": sum(1 for h in self.metrics["health_checks"] if h.get("status") == "healthy")
        }
    
    def save_metrics(self):
        """Save metrics to file"""
        self.calculate_summary()
        with open(self.log_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        print(f"✓ Metrics saved to {self.log_file}")
    
    def print_summary(self):
        """Print summary to console"""
        self.calculate_summary()
        summary = self.metrics["summary"]
        
        print("\n" + "="*70)
        print("📊 PRODUCTION MONITORING SUMMARY")
        print("="*70)
        print(f"Timestamp: {self.metrics['timestamp']}")
        print(f"API URL: {self.api_url}")
        print("\n📈 Statistics:")
        print(f"  Total Predictions: {summary.get('total_predictions', 0)}")
        print(f"  Success Rate: {summary.get('success_rate', '0%')}")
        print(f"  Avg Response Time: {summary.get('avg_response_time_ms', 0)}ms")
        print(f"  Min/Max Response: {summary.get('min_response_time_ms', 0)}/{summary.get('max_response_time_ms', 0)}ms")
        print(f"  Total Errors: {summary.get('total_errors', 0)}")
        print(f"  Health Checks Passed: {summary.get('health_checks_passed', 0)}")
        print("="*70 + "\n")


class UserFeedbackCollector:
    """Collect and analyze user feedback for model improvement"""
    
    def __init__(self, feedback_file: str = "user_feedback.json"):
        self.feedback_file = feedback_file
        self.feedback_data = self._load_feedback()
    
    def _load_feedback(self) -> Dict:
        """Load existing feedback"""
        if Path(self.feedback_file).exists():
            with open(self.feedback_file, 'r') as f:
                return json.load(f)
        return {
            "feedback_entries": [],
            "accuracy_corrections": [],
            "feature_requests": [],
            "bug_reports": [],
            "summary": {}
        }
    
    def add_prediction_feedback(self, prediction_id: str, actual_disease: str, 
                               predicted_disease: str, confidence: float, 
                               user_feedback: Optional[str] = None):
        """Record feedback on a prediction"""
        feedback = {
            "timestamp": datetime.now().isoformat(),
            "prediction_id": prediction_id,
            "predicted_disease": predicted_disease,
            "actual_disease": actual_disease,
            "confidence": confidence,
            "correct": predicted_disease.lower() == actual_disease.lower(),
            "user_comment": user_feedback
        }
        self.feedback_data["feedback_entries"].append(feedback)
        
        # Track as accuracy correction if wrong
        if not feedback["correct"]:
            self.feedback_data["accuracy_corrections"].append(feedback)
        
        return feedback
    
    def add_feature_request(self, feature: str, description: str, user_id: Optional[str] = None):
        """Record feature request"""
        request = {
            "timestamp": datetime.now().isoformat(),
            "feature": feature,
            "description": description,
            "user_id": user_id,
            "votes": 1
        }
        self.feedback_data["feature_requests"].append(request)
        return request
    
    def add_bug_report(self, bug: str, severity: str, steps_to_reproduce: Optional[str] = None):
        """Record bug report"""
        bug_report = {
            "timestamp": datetime.now().isoformat(),
            "bug_description": bug,
            "severity": severity,  # "critical", "high", "medium", "low"
            "steps_to_reproduce": steps_to_reproduce,
            "status": "new"
        }
        self.feedback_data["bug_reports"].append(bug_report)
        return bug_report
    
    def calculate_accuracy(self) -> Dict:
        """Calculate model accuracy from feedback"""
        entries = self.feedback_data["feedback_entries"]
        if not entries:
            return {"total": 0, "correct": 0, "accuracy": 0}
        
        correct = sum(1 for e in entries if e["correct"])
        return {
            "total": len(entries),
            "correct": correct,
            "accuracy": f"{(correct / len(entries) * 100):.1f}%"
        }
    
    def get_misclassified_diseases(self) -> Dict:
        """Get diseases that are frequently misclassified"""
        corrections = self.feedback_data["accuracy_corrections"]
        if not corrections:
            return {}
        
        misclassified = {}
        for correction in corrections:
            disease = correction["predicted_disease"]
            if disease not in misclassified:
                misclassified[disease] = {"count": 0, "correct_disease": []}
            misclassified[disease]["count"] += 1
            misclassified[disease]["correct_disease"].append(correction["actual_disease"])
        
        return misclassified
    
    def save_feedback(self):
        """Save feedback to file"""
        self.feedback_data["summary"] = {
            "total_feedback_entries": len(self.feedback_data["feedback_entries"]),
            "accuracy": self.calculate_accuracy(),
            "corrections_needed": len(self.feedback_data["accuracy_corrections"]),
            "feature_requests": len(self.feedback_data["feature_requests"]),
            "bug_reports": len(self.feedback_data["bug_reports"]),
            "last_updated": datetime.now().isoformat()
        }
        
        with open(self.feedback_file, 'w') as f:
            json.dump(self.feedback_data, f, indent=2)
        print(f"✓ Feedback saved to {self.feedback_file}")
    
    def print_report(self):
        """Print feedback report"""
        summary = self.feedback_data["summary"]
        accuracy = self.calculate_accuracy()
        
        print("\n" + "="*70)
        print("📋 USER FEEDBACK REPORT")
        print("="*70)
        print(f"Total Feedback Entries: {len(self.feedback_data['feedback_entries'])}")
        print(f"Model Accuracy (from feedback): {accuracy['accuracy']}")
        print(f"Corrections Needed: {len(self.feedback_data['accuracy_corrections'])}")
        print(f"Feature Requests: {len(self.feedback_data['feature_requests'])}")
        print(f"Bug Reports: {len(self.feedback_data['bug_reports'])}")
        
        if self.get_misclassified_diseases():
            print("\n🎯 Top Misclassified Diseases:")
            for disease, info in sorted(
                self.get_misclassified_diseases().items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )[:5]:
                print(f"  - {disease}: {info['count']} times")
        
        if self.feedback_data['feature_requests']:
            print("\n💡 Top Feature Requests:")
            for req in sorted(
                self.feedback_data['feature_requests'],
                key=lambda x: x.get('votes', 0),
                reverse=True
            )[:3]:
                print(f"  - {req['feature']}: {req['description']}")
        
        print("="*70 + "\n")


# Example usage
if __name__ == "__main__":
    # Production monitoring
    monitor = ProductionMonitor("https://symptom-checker-api-xxxxx.a.run.app")
    
    print("🔍 Running Production Health Checks...")
    monitor.health_check()
    
    # Test some predictions
    test_cases = [
        "fever and cough",
        "joint pain and stiffness",
        "shortness of breath and weakness"
    ]
    
    for test in test_cases:
        monitor.test_prediction(test)
    
    monitor.save_metrics()
    monitor.print_summary()
    
    # Feedback collection example
    feedback = UserFeedbackCollector()
    
    # Simulate user feedback
    feedback.add_prediction_feedback(
        "pred_001",
        "Flu",
        "Hypertension",
        0.58,
        "Actually had the flu, not hypertension"
    )
    
    feedback.add_feature_request(
        "Multilingual Support",
        "Add Spanish and Portuguese language support"
    )
    
    feedback.add_bug_report(
        "App crashes on some devices",
        "critical",
        "Use on Android 9 devices"
    )
    
    feedback.save_feedback()
    feedback.print_report()
