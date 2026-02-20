import 'package:flutter/foundation.dart';
import 'package:dio/dio.dart';

import '../models/prediction_response.dart';

class ApiService {
  ApiService({String? baseUrl})
  : _dio = Dio(BaseOptions(baseUrl: baseUrl ?? _defaultBaseUrl));

  static String get _defaultBaseUrl {
    if (kIsWeb) {
      return 'http://127.0.0.1:8001';
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return 'http://10.0.2.2:8001';
      default:
        return 'http://127.0.0.1:8001';
    }
  }

  final Dio _dio;

  Future<PredictionResponse> predict({
    required String text,
    required String language,
    Map<String, double> symptomIntensity = const {},
  }) async {
    final response = await _dio.post('/predict', data: {
      'text': text,
      'language': language,
      'symptom_intensity': symptomIntensity,
    });

    return PredictionResponse.fromJson(response.data as Map<String, dynamic>);
  }
}
