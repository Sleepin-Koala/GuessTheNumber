import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';


import 'package:app/core/theme/app_typography.dart';
import 'package:app/core/theme/app_icon.dart';
import 'package:app/core/theme/app_colors.dart';

import 'package:app/core/widgets/CartoonIcon.dart';
import 'package:app/core/widgets/Cartoon_icon_button.dart';

import 'package:app/features/game/bloc/game_cubit.dart';



class DuelVariantSelectView extends StatelessWidget {
  const DuelVariantSelectView({super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
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
                Text("DUEL", style: AppTypography.display(fontSize: 28)),
              ],
            ),
            const SizedBox(height: 24),
            Expanded(
              child: ListView(
                children: [
                  _VariantTile(
                    title: "ASYMÉTRIQUE",
                    description: "Cache un nombre, devine celui de l'adversaire. "
                        "Moins d'essais gagne le pari.",
                    color: AppColors.secondary,
                    enabled: true,
                    onTap: () {context.read<GameCubit>().startDuelMode();},
                  ),
                  const SizedBox(height: 14),
                  const _VariantTile(
                    title: "COURSE DE VITESSE",
                    description: "Même nombre, le premier qui trouve gagne.",
                    color: AppColors.cardBg,
                    enabled: false,
                  ),
                  const SizedBox(height: 14),
                  const _VariantTile(
                    title: "MIROIR",
                    description: "Même nombre, chacun son tour, comparaison des essais.",
                    color: AppColors.cardBg,
                    enabled: false,
                  ),
                  const SizedBox(height: 14),
                  const _VariantTile(
                    title: "ENCHÈRES",
                    description: "Mise plus haute = doit être plus rapide/précis.",
                    color: AppColors.cardBg,
                    enabled: false,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _VariantTile extends StatelessWidget {
  final String title;
  final String description;
  final Color color;
  final bool enabled;
  final VoidCallback? onTap;

  const _VariantTile({
    required this.title,
    required this.description,
    required this.color,
    required this.enabled,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Opacity(
      opacity: enabled ? 1.0 : 0.5,
      child: GestureDetector(
        onTap: enabled ? onTap : null,
        child: Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: Colors.black, width: 3),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(title, style: AppTypography.body(fontSize: 17, fontWeight: FontWeight.w800)),
                        if (!enabled) ...[
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.black26,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              "BIENTÔT",
                              style: AppTypography.body(fontSize: 9, color: Colors.white54, letterSpacing: 1),
                            ),
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      description,
                      style: AppTypography.body(fontSize: 13, color: Colors.white70, fontWeight: FontWeight.w500),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
