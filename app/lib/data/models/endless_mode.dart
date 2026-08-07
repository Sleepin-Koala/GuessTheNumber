class EndlessModeSession {
  final String sessionId;
  final int maxAttempt;
  final int attemptLeft;
  final int maxRange;
  final int bet;
  final int stage;
  final int playerCoins;

  const EndlessModeSession({
    required this.sessionId,
    required this.maxAttempt,
    required this.attemptLeft,
    required this.maxRange,
    required this.bet,
    required this.stage,
    required this.playerCoins
  });

  factory EndlessModeSession.fromJson(Map<String, dynamic> json) {
    return EndlessModeSession(
      sessionId: json['session_id'] as String,
      maxAttempt: json['max_attempt'] as int,
      attemptLeft: json['attempt_left'] as int,
      maxRange: json['max_range'] as int,
      bet: json['bet'] as int,
      stage: json['stage'] as int,
      playerCoins: json['coins'] as int,
    );
  }
}
