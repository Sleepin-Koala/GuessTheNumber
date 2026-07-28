enum GuessOutcome {PLUS , MOINS , OK}


class GuessResult {
  final GuessOutcome outcome;
  final int attemptLeft;
  final double distance;
  final String type;

  const GuessResult({
    required this.outcome,
    required this.attemptLeft,
    required this.distance,
    required this.type
  });

  factory GuessResult.fromJson(Map<String, dynamic> json) {
    final resultString = json['result'] as String;
    final GuessOutcome parsedOutcome;
    
    if (resultString == 'PLUS') {
      parsedOutcome = GuessOutcome.PLUS;
    } else if (resultString == 'MOINS') {
      parsedOutcome = GuessOutcome.MOINS;
    } else {
      parsedOutcome = GuessOutcome.OK;
    }

    return GuessResult(
      outcome: parsedOutcome,
      attemptLeft: json['attempt_left'] as int,
      distance: json['distance'] as double,
      type: json['type'] as String,
    );
  } 

}