class EndlessModeSession {
  final String sessionId;
  final int maxAttempt;
  final int attemptLeft;
  final int maxRange;
  final int timeLimit;
  final int bet;
  final int winnable;
  final int stage;

  const EndlessModeSession({
    required this.sessionId,
    required this.maxAttempt,
    required this.attemptLeft,
    required this.maxRange,
    required this.timeLimit,
    required this.bet,
    required this.winnable,
    required this.stage,
  });

  factory EndlessModeSession.fromJson(Map<String, dynamic> json) {
    return EndlessModeSession(
      sessionId: json['session_id'] as String,
      maxAttempt: json['max_attempt'] as int,
      attemptLeft: json['attempt_left'] as int,
      maxRange: json['max_range'] as int,
      timeLimit: json['time_limit'] as int,
      bet: json['bet'] as int,
      winnable: json['winnable'] as int,
      stage: json['stage'] as int,
    );
  }
}
