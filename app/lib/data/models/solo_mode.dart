class SoloModeSession {
  final String sessionId;
  final int maxAttempt;
  final int attemptLeft;
  final int maxRange;
  final int timeLimit;

  const SoloModeSession({
    required this.sessionId,
    required this.maxAttempt,
    required this.attemptLeft,
    required this.maxRange,
    required this.timeLimit,
  });

  factory SoloModeSession.fromJson(Map<String, dynamic> json) {
    return SoloModeSession(
      sessionId: json['session_id'] as String,
      maxAttempt: json['max_attempt'] as int,
      attemptLeft: json['attempt_left'] as int,
      maxRange: json['max_range'] as int,
      timeLimit: json['time_limit'] as int,
    );
  }
}

class EndSessionSoloMode {
  final int coins;
  final int xp;
  final int stars;

  const EndSessionSoloMode({required this.coins, required this.xp , required this.stars});

  factory EndSessionSoloMode.fromJson(Map<String, dynamic> json) {
    return EndSessionSoloMode(
      coins: json['coins'] as int,
      xp: json['xp'] as int,
      stars: json['stars'] as int,
    );
  }
}
