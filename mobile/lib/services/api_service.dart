import 'package:flutter/foundation.dart';
import 'package:dio/dio.dart';

import '../models/prediction_response.dart';

class ApiService {
  ApiService({String? baseUrl})
  : _dio = Dio(BaseOptions(baseUrl: baseUrl ?? _defaultBaseUrl));

  static String get _defaultBaseUrl {
    return 'https://symptom-checker-vhz9.onrender.com';
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
