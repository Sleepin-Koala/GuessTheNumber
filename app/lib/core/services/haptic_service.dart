import 'package:flutter/services.dart';
import 'settings_service.dart';

class HapticService {
  static Future<void> triggerKeyTap() async {
    if (SettingsService.hapticsEnabled) await HapticFeedback.lightImpact();
  }

  static Future<void> triggerErrorImpact() async {
    if (SettingsService.hapticsEnabled) await HapticFeedback.mediumImpact();
  }

  static Future<void> triggerSuccessBoom() async {
    if (SettingsService.hapticsEnabled) await HapticFeedback.vibrate();
  }
}