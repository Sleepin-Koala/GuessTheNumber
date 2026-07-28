import 'package:shared_preferences/shared_preferences.dart';


class SettingsService {

  const SettingsService();

  static const _keyHaptics = 'settings_haptics_enabled';
  static const _keySound = 'settings_sound_enabled';
  static const _keyMusic = 'settings_music_enabled';
  static const _playerId = "player_id";

  static bool hapticsEnabled = true;
  static bool soundEnabled = true;
  static bool musicEnabled = true;
  static String playerId = "";

  static Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    hapticsEnabled = prefs.getBool(_keyHaptics) ?? true;
    soundEnabled = prefs.getBool(_keySound) ?? true;
    musicEnabled = prefs.getBool(_keyMusic) ?? true;
    playerId = prefs.getString(_playerId)?? "";
  }

  static Future<void> setHapticsEnabled(bool value) async {
    hapticsEnabled = value; // mise à jour immédiate en mémoire (UI instantanée)
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_keyHaptics, value); // écriture disque en arrière-plan
  }

  static Future<void> setSoundEnabled(bool value) async {
    soundEnabled = value;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_keySound, value);
  }

  static Future<void> setMusicEnabled(bool value) async {
    musicEnabled = value;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_keyMusic, value);
  }

  static Future<void> setData(String playerId) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_playerId, playerId);
  }



}