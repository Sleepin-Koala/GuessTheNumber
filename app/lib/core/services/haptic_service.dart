import 'package:flutter/services.dart';

class HapticService {
  /// Une vibration ultra-légère et rapide.
  /// Parfait pour le clic sur les touches du clavier numérique (effet mécanique).
  static Future<void> triggerKeyTap() async {
    await HapticFeedback.lightImpact();
  }

  /// Une vibration moyenne, double ou plus marquée.
  /// Idéal quand le joueur se trompe (FastAPI renvoie Higher/Lower) pour marquer le coup.
  static Future<void> triggerErrorImpact() async {
    await HapticFeedback.mediumImpact();
  }

  /// Une vibration lourde ou une série de vibrations.
  /// Déclenché uniquement lors de l'état GameSuccess (Victoire !).
  static Future<void> triggerSuccessBoom() async {
    await HapticFeedback.vibrate();
  }
}