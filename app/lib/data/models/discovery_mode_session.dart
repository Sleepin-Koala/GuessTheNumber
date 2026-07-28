
class DiscoveryModeSession {
  final String sessionId;
  final int maxRange;

  const DiscoveryModeSession({
    required this.sessionId,
    required this.maxRange,
  });

  factory DiscoveryModeSession.fromJson(Map<String, dynamic> json) {
    return DiscoveryModeSession(
      sessionId: json['session_id'] as String,
      maxRange: json['max_range'] as int,
    );
  }
}
