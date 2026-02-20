import 'package:flutter/material.dart';

import '../models/prediction_response.dart';
import '../services/api_service.dart';
import '../services/speech_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  final TextEditingController _controller = TextEditingController();
  final ApiService _apiService = ApiService();
  final SpeechService _speechService = SpeechService();

  PredictionResponse? _result;
  bool _loading = false;
  bool _speechReady = false;
  String _lang = 'en';
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  static const Map<String, Map<String, String>> _labels = {
    'en': {
      'title': 'Symptom Checker',
      'subtitle': 'AI-Powered Health Assessment',
      'hint': 'Describe your symptoms...',
      'predict': 'Analyze Symptoms',
      'risk': 'Risk Level',
      'diet': 'Diet Recommendation',
      'listen': 'Voice Input',
      'detected': 'Detected Symptoms',
      'explainability': 'Symptom Influence',
      'recommended': 'Recommended Foods',
      'avoid': 'Foods to Avoid',
      'notes': 'Health Notes',
      'empty': 'Describe your symptoms to get started',
      'sleeping': 'Server is waking up. Please retry in about 30 seconds.',
    },
    'hi': {
      'title': 'लक्षण जाँच',
      'subtitle': 'AI-शक्तिचालित स्वास्थ्य मूल्यांकन',
      'hint': 'अपने लक्षण लिखें...',
      'predict': 'विश्लेषण करें',
      'risk': 'जोखिम स्तर',
      'diet': 'आहार सलाह',
      'listen': 'वॉयस इनपुट',
      'detected': 'पहचाने गए लक्षण',
      'explainability': 'लक्षण प्रभाव',
      'recommended': 'अनुशंसित खाद्य पदार्थ',
      'avoid': 'बचने योग्य खाद्य पदार्थ',
      'notes': 'स्वास्थ्य नोट्स',
      'empty': 'शुरुआत करने के लिए अपने लक्षणों का वर्णन करें',
      'sleeping': 'सर्वर चालू हो रहा है। कृपया लगभग 30 सेकंड बाद फिर प्रयास करें।',
    },
    'te': {
      'title': 'లక్షణ పరిశీలన',
      'subtitle': 'AI-శక్తిచేసిన ఆరోగ్య మూల్యాంకనం',
      'hint': 'మీ లక్షణాలను వ్రాయండి...',
      'predict': 'విశ్లేషణ చేయండి',
      'risk': 'ప్రమాద స్థాయి',
      'diet': 'ఆహార సిఫార్సు',
      'listen': 'వాయిస్ ఇన్‌పుట్',
      'detected': 'గుర్తించిన లక్షణాలు',
      'explainability': 'లక్షణ ప్రభావం',
      'recommended': 'సిఫారసు చేసిన ఆహారాలు',
      'avoid': 'తప్పించవలసిన ఆహారాలు',
      'notes': 'ఆరోగ్య గమనికలు',
      'empty': 'ప్రారంభించడానికి మీ లక్షణాలను వివరించండి',
      'sleeping': 'సర్వర్ మేల్కొంటోంది. దయచేసి సుమారు 30 సెకన్ల తర్వాత మళ్లీ ప్రయత్నించండి.',
    },
  };

  static const Map<String, String> _localeMap = {
    'en': 'en_US',
    'hi': 'hi_IN',
    'te': 'te_IN',
  };

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(duration: const Duration(milliseconds: 600), vsync: this);
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _fadeController, curve: Curves.easeInOut),
    );
    _initSpeech();
  }

  @override
  void dispose() {
    _controller.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  Future<void> _initSpeech() async {
    final ok = await _speechService.initialize();
    if (!mounted) return;
    setState(() => _speechReady = ok);
  }

  Future<void> _toggleListening() async {
    if (!_speechReady) return;

    if (_speechService.isListening) {
      await _speechService.stopListening();
      setState(() {});
      return;
    }

    await _speechService.startListening(
      localeId: _localeMap[_lang] ?? 'en_US',
      onResult: (words) {
        setState(() => _controller.text = words);
      },
    );
    setState(() {});
  }

  Future<void> _predict() async {
    final text = _controller.text.trim();
    final t = _labels[_lang]!;
    if (text.isEmpty) return;

    setState(() => _loading = true);
    _fadeController.reset();
    
    try {
      final response = await _apiService.predict(text: text, language: _lang);
      if (!mounted) return;
      setState(() => _result = response);
      _fadeController.forward();
    } on ApiSleepingException {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(t['sleeping']!),
          backgroundColor: Colors.orange.shade700,
          behavior: SnackBarBehavior.floating,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Prediction failed: $e'),
          backgroundColor: Colors.red.shade600,
          behavior: SnackBarBehavior.floating,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = _labels[_lang]!;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        elevation: 0,
        backgroundColor: _getHealthColor(context),
        foregroundColor: Colors.white,
        title: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(t['title']!, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            Text(t['subtitle']!, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w400)),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              color: Colors.white.withOpacity(0.2),
            ),
            child: DropdownButton<String>(
              value: _lang,
              underline: const SizedBox.shrink(),
              icon: const Icon(Icons.language, color: Colors.white, size: 20),
              items: const [
                DropdownMenuItem(value: 'en', child: Text('EN', style: TextStyle(color: Colors.black))),
                DropdownMenuItem(value: 'hi', child: Text('HI', style: TextStyle(color: Colors.black))),
                DropdownMenuItem(value: 'te', child: Text('TE', style: TextStyle(color: Colors.black))),
              ],
              onChanged: (value) {
                if (value != null) setState(() => _lang = value);
              },
              dropdownColor: Colors.white,
            ),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              _getHealthColor(context).withOpacity(0.05),
              isDark ? Colors.grey.shade900 : Colors.grey.shade50,
            ],
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: ListView(
            children: [
              // Input Section
              TextField(
                controller: _controller,
                maxLines: 4,
                decoration: InputDecoration(
                  hintText: t['hint'],
                  hintStyle: TextStyle(color: Colors.grey.shade500),
                  filled: true,
                  fillColor: isDark ? Colors.grey.shade800 : Colors.white,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: _getHealthColor(context).withOpacity(0.3)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: _getHealthColor(context), width: 2),
                  ),
                    // Prefix icon removed - using hintText instead
                    prefixIcon: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Icon(Icons.health_and_safety, color: _getHealthColor(context)),
                    ),
                ),
              ),
              const SizedBox(height: 16),
              
              // Action Buttons
              Row(
                children: [
                  ElevatedButton.icon(
                    onPressed: _speechReady ? _toggleListening : null,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _speechService.isListening ? Colors.orange : _getHealthColor(context),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    icon: Icon(_speechService.isListening ? Icons.mic_off : Icons.mic),
                    label: Text(t['listen']!),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: _loading || _controller.text.isEmpty ? null : _predict,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _getHealthColor(context),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        disabledBackgroundColor: Colors.grey.shade400,
                      ),
                      child: _loading
                          ? SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2.5,
                                valueColor: AlwaysStoppedAnimation(isDark ? Colors.white : Colors.blue.shade900),
                              ),
                            )
                          : Text(
                              t['predict']!,
                              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                            ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 28),
              
              // Result Section
              if (_result == null && !_loading)
                Center(
                  child: Column(
                    children: [
                      Icon(Icons.info_outline, size: 48, color: Colors.grey.shade400),
                      const SizedBox(height: 12),
                      Text(
                        t['empty']!,
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.grey.shade600, fontSize: 16),
                      ),
                    ],
                  ),
                )
              else if (_result != null)
                FadeTransition(
                  opacity: _fadeAnimation,
                  child: _buildResultCard(t),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Color _getHealthColor(BuildContext context) {
    return Color.lerp(Colors.blue.shade600, Colors.cyan.shade400, 0.3) ?? Colors.blue;
  }

  Widget _buildResultCard(Map<String, String> t) {
    final result = _result!;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return SingleChildScrollView(
      child: Column(
        children: [
          // Disease Card
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: _getHealthColor(context).withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Icon(Icons.medical_services_outlined, color: _getHealthColor(context), size: 28),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              result.predictedDisease,
                              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                            ),
                            Text(
                              'Predicted Condition',
                              style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  LinearProgressIndicator(
                    value: result.confidence,
                    minHeight: 8,
                    backgroundColor: Colors.grey.shade300,
                    valueColor: AlwaysStoppedAnimation(_getHealthColor(context)),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Confidence: ${(result.confidence * 100).toStringAsFixed(1)}%',
                    style: TextStyle(fontSize: 13, color: Colors.grey.shade700, fontWeight: FontWeight.w500),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          
          // Risk Level Card
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            color: _getRiskCardColor(result.riskLevel, isDark),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(_getRiskIcon(result.riskLevel), color: Colors.white, size: 28),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${t['risk']}: ${result.riskLevel}',
                          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                        ),
                        Text(
                          'Risk Score: ${result.riskScore.toStringAsFixed(2)}',
                          style: const TextStyle(fontSize: 13, color: Colors.white70),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          
          // Detected Symptoms
          _buildSectionCard(
            title: t['detected']!,
            icon: Icons.checklist_rtl,
            isDark: isDark,
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: result.detectedSymptoms
                  .map((symptom) => Chip(
                        label: Text(symptom.replaceAll('_', ' ').toTitleCase()),
                        backgroundColor: _getHealthColor(context).withOpacity(0.15),
                        labelStyle: TextStyle(color: _getHealthColor(context), fontWeight: FontWeight.w600),
                      ))
                  .toList(),
            ),
          ),
          const SizedBox(height: 16),
          
          // Explainability
          _buildSectionCard(
            title: t['explainability']!,
            icon: Icons.insights,
            isDark: isDark,
            child: Column(
              children: result.explainability
                  .map((e) {
                    final symptom = e.symptom.replaceAll('_', ' ').toTitleCase();
                    final contribution = e.contribution;
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 8.0),
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(symptom, style: const TextStyle(fontWeight: FontWeight.w500)),
                          ),
                          SizedBox(
                            width: 80,
                            child: LinearProgressIndicator(
                              value: contribution > 1 ? 1 : contribution,
                              backgroundColor: Colors.grey.shade300,
                              valueColor: AlwaysStoppedAnimation(Colors.orange.shade600),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            '${(contribution * 100).toStringAsFixed(0)}%',
                            style: TextStyle(fontSize: 12, color: Colors.grey.shade700, fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                    );
                  })
                  .toList(),
            ),
          ),
          const SizedBox(height: 16),
          
          // Diet Recommendations
          _buildSectionCard(
            title: t['diet']!,
            icon: Icons.restaurant,
            isDark: isDark,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildDietSubsection('✓ ${t['recommended']!}', result.diet.recommended, Colors.green),
                const SizedBox(height: 16),
                _buildDietSubsection('✗ ${t['avoid']!}', result.diet.avoid, Colors.red),
                const SizedBox(height: 16),
                _buildDietSubsection('📝 ${t['notes']!}', result.diet.notes, Colors.blue),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionCard({
    required String title,
    required IconData icon,
    required bool isDark,
    required Widget child,
  }) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: _getHealthColor(context).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(icon, color: _getHealthColor(context), size: 20),
                ),
                const SizedBox(width: 12),
                Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ],
            ),
            const SizedBox(height: 16),
            child,
          ],
        ),
      ),
    );
  }

  Widget _buildDietSubsection(String title, List<String> items, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: color),
        ),
        const SizedBox(height: 8),
        ...items.map((item) => Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Text(
                item,
                style: const TextStyle(fontSize: 13),
              ),
            )),
      ],
    );
  }

  Color _getRiskCardColor(String riskLevel, bool isDark) {
    switch (riskLevel) {
      case 'Low':
        return Colors.green.shade600;
      case 'Moderate':
        return Colors.amber.shade600;
      case 'High':
        return Colors.orange.shade600;
      case 'Critical':
        return Colors.red.shade600;
      default:
        return Colors.blue.shade600;
    }
  }

  IconData _getRiskIcon(String riskLevel) {
    switch (riskLevel) {
      case 'Low':
        return Icons.sentiment_very_satisfied;
      case 'Moderate':
        return Icons.sentiment_neutral;
      case 'High':
        return Icons.sentiment_dissatisfied;
      case 'Critical':
        return Icons.warning;
      default:
        return Icons.info;
    }
  }
}

extension StringExtension on String {
  String toTitleCase() => split(' ').map((word) => '${word[0].toUpperCase()}${word.substring(1)}').join(' ');
}
