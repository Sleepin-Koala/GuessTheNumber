import 'package:app/core/theme/app_colors.dart';
import 'package:app/core/widgets/CartoonButton.dart';
import 'package:app/features/game/bloc/game_cubit.dart';
import 'package:app/features/game/bloc/game_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:lucide_icons/lucide_icons.dart';

class ClassicWinView extends StatelessWidget {
  const ClassicWinView({super.key});

  @override
  Widget build(BuildContext context) {
    final Color headerColor = AppColors.success;
    final Color shadowHeaderColor = const Color(0xFF1B5E20);
    final String title = 'VICTOIRE !';
    final IconData icon = LucideIcons.trophy;
    final state = context.read<GameCubit>().state;
    if (state is! GameClassicWin) return SizedBox.shrink();
    final attempts = state.finalAttemptsUsed;

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
                  "Tu as trouvé le nombre secret !",
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 18, color: Colors.white70),
                ),
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
            ),
          ),

          const Spacer(),

          Row(
            children: [
              CartoonButton(
                onPressed: () {
                  context.read<GameCubit>().onLevelSelection();
                },
                color: AppColors.primary,
                shadowColor: AppColors.secondary,
                child: Icon(LucideIcons.layers, color: Colors.white),
              ),

              CartoonButton(
                onPressed: () {
                  context.read<GameCubit>().startClassicSession(level: state.currentLevel+1);
                },
                color: AppColors.primary,
                shadowColor: AppColors.secondary,
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'NIVEAU SUIVANT',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    SizedBox(width: 12),
                    Icon(LucideIcons.moveRight, color: Colors.white),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
