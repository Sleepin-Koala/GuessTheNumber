




class GameSession {
  final String sessionId;
  final int maxAttempt;
  final int attemptLeft;
  final int maxRange;
  final int timeLimit;

  const GameSession({
    required this.sessionId,
    required this.maxAttempt,
    required this.attemptLeft,
    required this.maxRange,
    required this.timeLimit,
  });

  factory GameSession.fromJson(Map<String, dynamic> json) {
    return GameSession(
      sessionId: json['session_id'] as String,
      maxAttempt: json['max_attempt'] as int,
      attemptLeft: json['attempt_left'] as int,
      maxRange: json['max_range'] as int,
      timeLimit: json['time_limit'] as int,
    );
  }
}
