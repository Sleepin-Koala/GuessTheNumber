import 'package:app/features/game/bloc/game_cubit.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import "../../../../core/theme/app_colors.dart";
import 'package:lucide_icons/lucide_icons.dart';
import "../../../../core/widgets/CartoonButton.dart";


class DiscoverModeWinView extends StatelessWidget {
  final int attempts;
  const DiscoverModeWinView({super.key, required this.attempts});

  @override
  Widget build(BuildContext context) {
    final Color headerColor =  AppColors.success ;
    final Color shadowHeaderColor = const Color(0xFF1B5E20);
      
    final String title = 'VICTOIRE !';
    final IconData icon = LucideIcons.trophy;

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
                Text("Tu as trouvé le nombre secret !",
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 18, color: Colors.white70),
                ),
                ...[
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
              context.read<GameCubit>().onDiscoveryPage();
            },
            color: AppColors.primary,
            shadowColor: AppColors.secondary,
            child: const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(LucideIcons.repeat, color: Colors.white),
                SizedBox(width: 12),
                Text(
                  'REJOUER',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900),
                ),
              ],
            ),
          ),
        
          const SizedBox(height: 40),
          CartoonButton(
            onPressed: () {
              context.read<GameCubit>().onMenu();
            },
            color: AppColors.primary,
            shadowColor: AppColors.secondary,
            child: const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(LucideIcons.home, color: Colors.white),
                SizedBox(width: 12),
                Text(
                  'RETOUR A L\'ACCEUIL',
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
