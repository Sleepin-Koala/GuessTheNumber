import 'dart:convert';
import "../models/GameSession.dart";
import "../models/GuessOutCome.dart";
import "../models/player.dart";
import "../../core/network/api.dart";
import "package:http/http.dart" as http;

class GameRepository {
  final http.Client _httpClient;

  GameRepository({http.Client? httpClient})
    : _httpClient = httpClient ?? http.Client();

  Future<GameSession> StartSoloGame({
    required String playerId,
    required int level,
  }) async {
    final url = Uri.parse("${Api.baseUrl}/game/level");

    try {
      final response = await _httpClient.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"player_id": playerId, "level": level}),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> json = jsonDecode(response.body);
        return GameSession.fromJson(json);
      } else {
        throw Exception(
          'Impossible de démarrer le niveau $level (Code: ${response.statusCode})',
        );
      }
    } catch (e) {
      throw Exception('Erreur réseau lors du démarrage de la partie : $e');
    }
  }

  /// POST /game/guess
  Future<GuessResult> makeGuess({
    required String sessionId,
    required String playerId,
    required int number,
  }) async {
    final url = Uri.parse('${Api.baseUrl}/game/guess');

    try {
      final response = await _httpClient.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'session_id': sessionId,
          'player_id': playerId,
          'number': number,
        }),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> json = jsonDecode(response.body);
        return GuessResult.fromJson(json);
      } else {
        throw Exception(
          'Échec de la soumission du nombre (Code: ${response.statusCode})',
        );
      }
    } catch (e) {
      throw Exception('Erreur réseau lors de la soumission : $e');
    }
  }

  /// POST /game/endlevel
  Future<Player> endGameSession({
    required String sessionId,
    required String playerId,
    required String status, // 'win' | 'lose' | 'abandoned'
    required int levelPlayed,
  }) async {
    final url = Uri.parse('${Api.baseUrl}/game/endlevel');

    try {
      final response = await _httpClient.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'session_id': sessionId,
          'player_id': playerId,
          'status': status,
          'ended':
              DateTime.now().millisecondsSinceEpoch /
              1000, // Timestamp secondes
          'levelPlayed': levelPlayed,
        }),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> json = jsonDecode(response.body);
        return Player.fromJson(json);
      } else {
        throw Exception(
          'Impossible de clôturer la partie (Code: ${response.statusCode})',
        );
      }
    } catch (e) {
      throw Exception('Erreur réseau lors de la clôture de la partie : $e');
    }
  }
}
