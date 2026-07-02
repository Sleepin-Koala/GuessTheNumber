

import 'package:flutter/widgets.dart';

class GameMode {
  final String id;
  final String title;
  final String description;
  final IconData icon;
  final Color color;
  final Color gradientEnd;
  final Color shadowColor;
  

  const GameMode({
    required this.id,
    required this.title,
    required this.description,
    required this.icon,
    required this.color,
    required this.gradientEnd,
    required this.shadowColor,
  });
}