import 'package:speech_to_text/speech_to_text.dart';

class SpeechService {
  final SpeechToText _speech = SpeechToText();

  Future<bool> initialize() async {
    return _speech.initialize();
  }

  bool get isListening => _speech.isListening;

  Future<void> startListening({
    required String localeId,
    required void Function(String words) onResult,
  }) async {
    await _speech.listen(
      localeId: localeId,
      onResult: (result) => onResult(result.recognizedWords),
      listenOptions: SpeechListenOptions(
        partialResults: true,
        cancelOnError: true,
      ),
    );
  }

  Future<void> stopListening() async {
    await _speech.stop();
  }
}
