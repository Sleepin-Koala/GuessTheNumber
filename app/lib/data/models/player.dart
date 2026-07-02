class Player {
  final String id;
  final String name;
  final int xp;
  final int gems;
  final int coins;
  final int level;

  const Player({
    required this.id,
    required this.name,
    required this.xp,
    required this.gems,
    required this.coins,
    required this.level,
  });

  factory Player.fromJson(Map<String, dynamic> json) {
    return (Player(
      id: json["id"] as String,
      name: json["name"] as String,
      xp: json["xp"] as int,
      gems: json["gems"] as int,
      coins: json["coins"] as int,
      level: json["level"] as int,
    ));
  }
}
