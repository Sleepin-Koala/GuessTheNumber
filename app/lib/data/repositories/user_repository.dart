import "dart:convert";

import "package:app/core/network/api.dart";
import "package:app/data/models/player.dart";
import "package:http/http.dart" as http;

class UserRepository {
  final http.Client _httpClient;

  UserRepository({http.Client? httpClient})
    : _httpClient = httpClient ?? http.Client();

  Future<Player> getNewPlayer() async {
    final url = Uri.parse("${Api.baseUrl}/user/new_player");
    
    try {
      final response = await _httpClient.get(url);

      if (response.statusCode == 200) {
        final Map<String, dynamic> json = jsonDecode(response.body);
        return Player.fromJson(json);
      } else {
        throw Exception(
          'Impossible de cree le joueur (Code: ${response.statusCode})',
        );
      }
    } catch (e) {
      throw Exception('Erreur réseau lors du démarrage de la partie : $e');
    }
  }
}
