class ExplainabilityItem {
  final String symptom;
  final double contribution;

  ExplainabilityItem({required this.symptom, required this.contribution});

  factory ExplainabilityItem.fromJson(Map<String, dynamic> json) {
    return ExplainabilityItem(
      symptom: json['symptom'] as String,
      contribution: (json['contribution'] as num).toDouble(),
    );
  }
}

class DietPlan {
  final List<String> recommended;
  final List<String> avoid;
  final List<String> notes;

  DietPlan({required this.recommended, required this.avoid, required this.notes});

  factory DietPlan.fromJson(Map<String, dynamic> json) {
    return DietPlan(
      recommended: (json['recommended'] as List).map((e) => e.toString()).toList(),
      avoid: (json['avoid'] as List).map((e) => e.toString()).toList(),
      notes: (json['notes'] as List).map((e) => e.toString()).toList(),
    );
  }
}

class PredictionResponse {
  final String predictedDisease;
  final double confidence;
  final List<Map<String, double>> topK;
  final String riskLevel;
  final double riskScore;
  final List<ExplainabilityItem> explainability;
  final List<String> detectedSymptoms;
  final DietPlan diet;

  PredictionResponse({
    required this.predictedDisease,
    required this.confidence,
    required this.topK,
    required this.riskLevel,
    required this.riskScore,
    required this.explainability,
    required this.detectedSymptoms,
    required this.diet,
  });

  factory PredictionResponse.fromJson(Map<String, dynamic> json) {
    final topKRaw = (json['top_k'] as List)
        .map((entry) => (entry as Map<String, dynamic>).map(
              (key, value) => MapEntry(key, (value as num).toDouble()),
            ))
        .toList();

    return PredictionResponse(
      predictedDisease: json['predicted_disease'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      topK: topKRaw,
      riskLevel: json['risk_level'] as String,
      riskScore: (json['risk_score'] as num).toDouble(),
      explainability: (json['explainability'] as List)
          .map((e) => ExplainabilityItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      detectedSymptoms:
          (json['detected_symptoms'] as List).map((e) => e.toString()).toList(),
      diet: DietPlan.fromJson(json['diet'] as Map<String, dynamic>),
    );
  }
}
