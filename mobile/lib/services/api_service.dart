import 'package:dio/dio.dart';

import '../models/prediction_response.dart';

class ApiSleepingException implements Exception {
  const ApiSleepingException([
    this.message = 'API is waking up. Please retry in about 30 seconds.',
  ]);

  final String message;

  @override
  String toString() => message;
}

class ApiService {
  ApiService({String? baseUrl})
  : _dio = Dio(
      BaseOptions(
        baseUrl: baseUrl ?? _defaultBaseUrl,
        connectTimeout: const Duration(seconds: 20),
        receiveTimeout: const Duration(seconds: 35),
        sendTimeout: const Duration(seconds: 20),
      ),
    );

  static String get _defaultBaseUrl {
    return 'https://symptom-checker-vhz9.onrender.com';
  }

  final Dio _dio;

  Future<PredictionResponse> predict({
    required String text,
    required String language,
    Map<String, double> symptomIntensity = const {},
  }) async {
    try {
      final response = await _dio.post('/predict', data: {
        'text': text,
        'language': language,
        'symptom_intensity': symptomIntensity,
      });

      return PredictionResponse.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      if (_isLikelyColdStart(e)) {
        throw const ApiSleepingException();
      }
      rethrow;
    }
  }

  bool _isLikelyColdStart(DioException error) {
    final statusCode = error.response?.statusCode;

    if (statusCode == 502 || statusCode == 503 || statusCode == 504) {
      return true;
    }

    return error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        error.type == DioExceptionType.sendTimeout ||
        error.type == DioExceptionType.connectionError;
  }
}
