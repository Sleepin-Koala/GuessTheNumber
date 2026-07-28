import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_icon.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/widgets/cartoon_icon_button.dart';
import '../bloc/game_cubit.dart';
import '../../../core/widgets/CartoonIcon.dart';
import '../../../core/services/settings_service.dart';

class OptionsView extends StatefulWidget {
  const OptionsView({super.key});

  @override
  State<OptionsView> createState() => _OptionsViewState();
}

class _OptionsViewState extends State<OptionsView> {
  late bool _haptics = SettingsService.hapticsEnabled;
  late bool _sound = SettingsService.soundEnabled;
  late bool _music = SettingsService.musicEnabled;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              CartoonIconButton(
                size: 48,
                child: const CartoonIcon(AppIcons.close, size: 20),
                onPressed: () => context.read<GameCubit>().resetToHome(),
              ),
              const SizedBox(width: 16),
              Text("OPTIONS", style: AppTypography.display(fontSize: 28)),
            ],
          ),
          const SizedBox(height: 28),
    
          _SectionLabel("GAMEPLAY"),
          _SettingSwitchTile(
            title: "Vibrations",
            subtitle: "Retour haptique sur les touches et résultats",
            value: _haptics,
            onChanged: (v) {
              setState(() => _haptics = v);
              SettingsService.setHapticsEnabled(v);
            },
          ),
    
          const SizedBox(height: 12),
          _SectionLabel("AUDIO"),
          _SettingSwitchTile(
            title: "Effets sonores",
            subtitle: "Bientôt disponible",
            value: _sound,
            onChanged: (v) {
              setState(() => _sound = v);
              SettingsService.setSoundEnabled(v);
            },
          ),
          _SettingSwitchTile(
            title: "Musique",
            subtitle: "Bientôt disponible",
            value: _music,
            onChanged: (v) {
              setState(() => _music = v);
              SettingsService.setMusicEnabled(v);
            },
          ),
    
          const SizedBox(height: 12),
          _SectionLabel("DONNÉES"),
          _DangerActionTile(
            title: "Réinitialiser ma progression",
            onTap: () {},
          ),
    
          const Spacer(),
    
          Center(
            child: Text(
              "Guess The Number — v0.1.0",
              style: AppTypography.body(fontSize: 12, color: Colors.white24),
            ),
          ),
        ],
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final String label;
  const _SectionLabel(this.label);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, left: 4),
      child: Text(
        label,
        style: AppTypography.body(
          fontSize: 12,
          fontWeight: FontWeight.w800,
          color: AppColors.primary,
          letterSpacing: 1.5,
        ),
      ),
    );
  }
}

class _SettingSwitchTile extends StatelessWidget {
  final String title;
  final String subtitle;
  final bool value;
  final ValueChanged<bool> onChanged;

  const _SettingSwitchTile({
    required this.title,
    required this.subtitle,
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.black, width: 3),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: AppTypography.body(fontSize: 16, fontWeight: FontWeight.w800)),
                const SizedBox(height: 2),
                Text(subtitle, style: AppTypography.body(fontSize: 12, color: Colors.white54)),
              ],
            ),
          ),
          Switch.adaptive(
            value: value,
            onChanged: onChanged,
            activeColor: AppColors.primary,
          ),
        ],
      ),
    );
  }
}

class _DangerActionTile extends StatelessWidget {
  final String title;
  final VoidCallback onTap;

  const _DangerActionTile({required this.title, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
        decoration: BoxDecoration(
          color: AppColors.cardBg,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.danger, width: 3),
        ),
        child: Row(
          children: [
            CartoonIcon(AppIcons.refresh, size: 20),
            const SizedBox(width: 12),
            Text(
              title,
              style: AppTypography.body(
                fontSize: 15,
                fontWeight: FontWeight.w800,
                color: AppColors.danger,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
