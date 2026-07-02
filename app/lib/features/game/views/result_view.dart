import 'package:app/features/game/bloc/game_cubit.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import "../../../core/theme/app_colors.dart";
import 'package:lucide_icons/lucide_icons.dart';
import "../../../core/widgets/CartoonButton.dart";


class ResultView extends StatelessWidget {
  final bool isWin;
  final int? attempts;
  const ResultView({super.key, required this.isWin, this.attempts});

  @override
  Widget build(BuildContext context) {
    final Color headerColor = isWin ? AppColors.success : AppColors.danger;
    final Color shadowHeaderColor = isWin
        ? const Color(0xFF1B5E20)
        : const Color(0xFFB71C1C);
    final String title = isWin ? 'VICTOIRE !' : 'DÉFAITE...';
    final IconData icon = isWin ? LucideIcons.trophy : LucideIcons.frown;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 40.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: headerColor,
              borderRadius: BorderRadius.circular(32),
              border: Border.all(color: Colors.black, width: 4),
              boxShadow: [
                BoxShadow(
                  color: shadowHeaderColor,
                  offset: const Offset(0, 8),
                  blurRadius: 0,
                ),
              ],
            ),
            child: Column(
              children: [
                Icon(icon, size: 80, color: Colors.white),
                const SizedBox(height: 16),
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 36,
                    fontWeight: FontWeight.w900,
                    color: Colors.white,
                    letterSpacing: 2,
                    shadows: [
                      Shadow(
                        color: Colors.black,
                        offset: Offset(2, 2),
                        blurRadius: 0,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 40),

          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AppColors.cardBg,
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: Colors.black, width: 3),
            ),

            child: Column(
              children: [
                Text(
                  isWin
                      ? "Tu as trouvé le nombre secret !"
                      : "Tu as épuisé toutes tes tentatives...",
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 18, color: Colors.white70),
                ),
                if (isWin && attempts != null) ...[
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        LucideIcons.zap,
                        color: AppColors.primary,
                        size: 24,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Essais utilisés : $attempts',
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.w900,
                          color: AppColors.primary,
                        ),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        
          const Spacer(),

          CartoonButton(
            onPressed: () {
              // context.read<GameCubit>().resetToHome();
            },
            color: AppColors.primary,
            shadowColor: AppColors.secondary,
            child: const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(LucideIcons.home, color: Colors.white),
                SizedBox(width: 12),
                Text(
                  'RETOUR À L\'ACCUEIL',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900),
                ),
              ],
            ),
          )
        ],
      ),
    );
  }
}
