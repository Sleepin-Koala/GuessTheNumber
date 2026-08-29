import 'dart:convert';
import "package:app/data/models/discovery_mode_session.dart";
import "package:app/data/models/duel_room.dart";

import "../models/solo_mode.dart";
import "../models/endless_mode.dart";
import "../models/GuessOutCome.dart";
import "../models/player.dart";

import "../../core/network/api.dart";
import "package:http/http.dart" as http;

class GameRepository {
  final http.Client _httpClient;
  late EndlessModeRepo endlessMode;
  late DiscoveryModeRepo discoveryMode;
  late SoloModeRepo soloMode;
  late DuelModeRepo duelMode;

  GameRepository({http.Client? httpClient})
    : _httpClient = httpClient ?? http.Client() {
    endlessMode = EndlessModeRepo(_httpClient);
    discoveryMode = DiscoveryModeRepo(_httpClient);
    soloMode = SoloModeRepo(_httpClient);
    duelMode = DuelModeRepo(_httpClient);
  }

  //solo

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

  Future<Player> endGameSession({
    required String sessionId,
    required String playerId,
    required String status, // 'win' | 'lose' | 'abandoned'
    required int? levelPlayed,
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

class EndlessModeRepo {
  final http.Client _httpclient;

  EndlessModeRepo(this._httpclient);

  Future<int> endGameSession({
    required String sessionId,
    required String playerId,
    required String status, // 'win' | 'lose' | 'abandoned'
  }) async {
    final url = Uri.parse('${Api.baseUrl}/game/endless/end_session');

    try {
      final response = await _httpclient.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'session_id': sessionId,
          'player_id': playerId,
          'status': status,
          'ended':
              DateTime.now().millisecondsSinceEpoch /
              1000, // Timestamp secondes
        }),
      );

      if (response.statusCode == 200) {
        final int res = jsonDecode(response.body);
        return res;
      } else {
        throw Exception(
          'Impossible de clôturer la partie (Code: ${response.statusCode})',
        );
      }
    } catch (e) {
      throw Exception('Erreur réseau lors de la clôture de la partie : $e');
    }
  }

  Future<EndlessModeSession> start({player_id, bet, stage}) async {
    final url = Uri.parse("${Api.baseUrl}/game/endless/start");

    try {
      final response = await _httpclient.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"player_id": player_id, "bet": bet, "stage": stage}),
      );

      if (response.statusCode == 200) {
        Map<String, dynamic> json = jsonDecode(response.body);
        return EndlessModeSession.fromJson(json);
      } else {
        throw Exception(
          'Impossible de démarrer le niveau  (Code: ${response.statusCode})',
        );
      }
    } catch (e) {
      throw Exception('Erreur réseau lors du démarrage de la partie : $e');
    }
  }

  Future<Player> collect({playerId}) async {
    final url = Uri.parse('${Api.baseUrl}/game/endless/collect');

    try {
      final response = await _httpclient.post(
        url,
        body: jsonEncode({"player_id": playerId}),
      );

      if (response.statusCode == 200) {
        return Player.fromJson(jsonDecode(response.body));
      } else {
        throw Exception(
          'Impossible de clôturer la partie (Code: ${response.statusCode})',
        );
      }
    } catch (e) {
      throw Exception('Erreur réseau lors de la clôture de la partie : $e');
    }
  }

  Future<Player> guess({sessionId, playerId, number}) async {
    final url = Uri.parse('${Api.baseUrl}/game/endless/guess');

    try {
      final response = await _httpclient.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'session_id': sessionId,
          'player_id': playerId,
          'status': number,
          'ended':
              DateTime.now().millisecondsSinceEpoch /
              1000, // Timestamp secondes
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

class DiscoveryModeRepo {
  final http.Client _httpclient;

  DiscoveryModeRepo(this._httpclient);

  Future<int> endGameSession({
    required String sessionId,
    required String playerId,
  }) async {
    final url = Uri.parse('${Api.baseUrl}/game/discovery/end_session');

    try {
      final response = await _httpclient.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'session_id': sessionId,
          'player_id': playerId,
          'ended':
              DateTime.now().millisecondsSinceEpoch /
              1000, // Timestamp secondes
        }),
      );

      if (response.statusCode == 200) {
        final int res = jsonDecode(response.body);
        return res;
      } else {
        throw Exception(
          'Impossible de clôturer la partie (Code: ${response.statusCode})',
        );
      }
    } catch (e) {
      throw Exception('Erreur réseau lors de la clôture de la partie : $e');
    }
  }

  Future<DiscoveryModeSession> start({player_id, max_range}) async {
    final url = Uri.parse("${Api.baseUrl}/game/discovery/start");

    try {
      final response = await _httpclient.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"player_id": player_id, "max_range": max_range}),
      );

      if (response.statusCode == 200) {
        Map<String, dynamic> json = jsonDecode(response.body);
        return DiscoveryModeSession.fromJson(json);
      } else {
        throw Exception(
          'Impossible de démarrer le niveau  (Code: ${response.statusCode})',
        );
      }
    } catch (e) {
      throw Exception('Erreur réseau lors du démarrage de la partie : $e');
    }
  }
}

class SoloModeRepo {
  final http.Client _httpclient;

  SoloModeRepo(this._httpclient);

  Future<EndSessionSoloMode> endlevel({
    required String sessionId,
    required String playerId,
    required String status,
    required int levelPlayed,
  }) async {
    final url = Uri.parse('${Api.baseUrl}/game/classic/end_level');

    try {
      final response = await _httpclient.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'session_id': sessionId,
          'player_id': playerId,
          'status': status,
          'level_played': levelPlayed,
          'ended':
              DateTime.now().millisecondsSinceEpoch /
              1000, // Timestamp secondes
        }),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> json = jsonDecode(response.body);
        return EndSessionSoloMode.fromJson(json);
      } else {
        throw Exception(
          'Impossible de clôturer la partie (Code: ${response.statusCode})',
        );
      }
    } catch (e) {
      throw Exception('Erreur réseau lors de la clôture de la partie : $e');
    }
  }

  Future<SoloModeSession> start({
    required String playerId,
    required int level,
  }) async {
    final url = Uri.parse("${Api.baseUrl}/game/classic/level");

    try {
      final response = await _httpclient.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"player_id": playerId, "level": level}),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> json = jsonDecode(response.body);
        return SoloModeSession.fromJson(json);
      } else {
        throw Exception(
          'Impossible de démarrer le niveau $level (Code: ${response.statusCode})',
        );
      }
    } catch (e) {
      throw Exception('Erreur réseau lors du démarrage de la partie : $e');
    }
  }
}

class DuelModeRepo {
  final http.Client _httpclient;
  DuelModeRepo(this._httpclient);

  Future<List<DuelRoom>> fetchDuelRooms() async {
    final url = Uri.parse('${Api.baseUrl}/game/duel/rooms');

    try {
      final response = await _httpclient.get(url);

      if (response.statusCode == 200) {
        final List<dynamic> list = jsonDecode(response.body);
        return list.map((element) => DuelRoom.fromjson(element)).toList();
      } else {
        throw Exception(
          'Impossible de clôturer la partie (Code: ${response.statusCode})',
        );
      }
    } catch (e) {
      throw Exception('Erreur réseau lors de la clôture de la partie : $e');
    }
  }

  Future<DuelRoom> createDuelRoom(playerId, roomName, amount, maxRange) async {
    final url = Uri.parse('${Api.baseUrl}/game/duel/host');
    try {
      final response = await _httpclient.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'host_id': playerId,
          'name': roomName,
          'amount': amount,
          "max_range": maxRange,
        }),
      );

      if (response.statusCode == 200) {
        return DuelRoom.fromjson(jsonDecode(response.body));
      } else {
        throw Exception(
          'Impossible de clôturer la partie (Code: ${response.statusCode})',
        );
      }
    } catch (e) {
      throw Exception('Erreur réseau lors de la clôture de la partie : $e');
    }
  }

  Future<DuelRoom> checkRoomStatus(roomId) async {
    final url = Uri.parse('${Api.baseUrl}/game/duel/status');

    try {
      final response = await _httpclient.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"room_id": roomId}),
      );
      return DuelRoom.fromjson(jsonDecode(response.body));
    } catch (e) {
      throw Exception('Erreur réseau lors de la clôture de la partie : $e');
    }
  }

  Future<DuelRoom> joinDuelRoom(roomId, playerId) async {
    final url = Uri.parse('${Api.baseUrl}/game/duel/join');

    try {
      final response = await _httpclient.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"room_id": roomId, "player_id": playerId}),
      );
      return DuelRoom.fromjson(jsonDecode(response.body));
    } catch (e) {
      throw Exception('Erreur réseau lors de la clôture de la partie : $e');
    }
  }

  Future<DuelRoom> submitHiddenNumber({
    required String roomId,
    required String playerId,
    required int secretNumber,
  }) async {
    final url = Uri.parse('${Api.baseUrl}/game/duel/rooms/$roomId/hide');
    try {
      final response = await _httpclient.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"player_id": playerId, "number": secretNumber}),
      );
      if (response.statusCode == 200) {
        return DuelRoom.fromjson(jsonDecode(response.body));
      }
      throw Exception(
        'Impossible de cacher le nombre (Code: ${response.statusCode})',
      );
    } catch (e) {
      throw Exception('Erreur réseau : $e');
    }
  }

  Future<DuelRoom> submitDuelGuess({
    required String roomId,
    required String playerId,
    required int number,
  }) async {
    final url = Uri.parse('${Api.baseUrl}/game/duel/rooms/$roomId/guess');
    try {
      final response = await _httpclient.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"player_id": playerId, "number": number}),
      );
      if (response.statusCode == 200) {
        return DuelRoom.fromjson(jsonDecode(response.body));
      }
      throw Exception('Impossible de deviner (Code: ${response.statusCode})');
    } catch (e) {
      throw Exception('Erreur réseau : $e');
    }
  }

  Future<void> leaveDuelRoom({
    required String roomId,
    required String playerId,
  }) async {
    final url = Uri.parse('${Api.baseUrl}/duel/rooms/$roomId/leave');
    try {
      await _httpclient.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"player_id": playerId}),
      );
    } catch (_) {}
  }
}
