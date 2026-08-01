
enum DuelStatus {
  waiting, // room créée, en attente d'un 2e joueur
  round1Hide, // manche 1 : le hider doit cacher un nombre
  round1Guess, // manche 1 : le guesser doit deviner
  round2Hide, // manche 2 : rôles inversés
  round2Guess,
  finished, // partie terminée, winnerId renseigné
}

DuelStatus _statusFromString(String s) {
  switch (s) {
    case 'waiting':
      return DuelStatus.waiting;
    case 'round1_hide':
      return DuelStatus.round1Hide;
    case 'round1_guess':
      return DuelStatus.round1Guess;
    case 'round2_hide':
      return DuelStatus.round2Hide;
    case 'round2_guess':
      return DuelStatus.round2Guess;
    case 'finished':
      return DuelStatus.finished;
    default:
      throw Exception('Statut de duel inconnu: $s');
  }
}

class DuelRoom {
  final String room_id;
  final String host_id;
  final String? guess_id;
  final String room_name;
  final int betAmount;
  final DuelStatus status;
  final int MaxRange;
  final String? currentHiderId;
  final String? currentGuesserId;
  final double? lastDistance;
  final String? lastFeedback;
  final int? round1AttemptsUsed;
  final int? round2AttemptsUsed;
  final String? winnerId;


  DuelRoom({
    required this.room_id,
    required this.host_id,
    this.guess_id,
    required this.room_name,
    required this.betAmount,
    required this.status,
    required this.MaxRange,
    this.currentHiderId,
    this.currentGuesserId,
    this.lastDistance,
    this.lastFeedback,
    this.round1AttemptsUsed,
    this.round2AttemptsUsed,
    this.winnerId
  });



  factory DuelRoom.fromjson(Map<String, dynamic> json) {
    return (DuelRoom(
      room_id: json["room_id"] as String,
      host_id: json["host_id"] as String,
      guess_id: json["guess_id"] as String?,
      room_name: json["room_name"] as String,
      betAmount: json["bet_amount"] as int,
      status: _statusFromString(json["status"]),
      MaxRange : json["max_range"] as int,
      currentHiderId: json["current_hider_id"] as String?,
      currentGuesserId: json["current_guesser_id"] as String?,
      lastDistance: json["last_distance"] as double?,
      lastFeedback: json["last_feedback"] as String?,
      round1AttemptsUsed: json["round1_attempts_used"] as int?,
      round2AttemptsUsed: json["round2_attempts_used"] as int?,
      winnerId: json["winner_id"] as String?,
    ));
  }
}
