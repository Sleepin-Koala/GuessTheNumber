import 'package:flutter/material.dart';
import '../../data/models/player.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';
import './CartoonIcon.dart';
import '../theme/app_icon.dart';

class PlayerProgressBanner extends StatelessWidget {
  final Player player;

  const PlayerProgressBanner({super.key, required this.player});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 60,
      padding: const EdgeInsets.symmetric(horizontal: 12),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: Colors.black, width: 3),
        boxShadow: const [
          BoxShadow(color: Colors.black, offset: Offset(0, 4), blurRadius: 0),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
              color: AppColors.primary,
              shape: BoxShape.circle,
              border: Border.all(color: Colors.black, width: 2.5),
            ),
            child: Center(
              child: Text(
                "${player.level}",
                style: AppTypography.display(fontSize: 18, color: Colors.black),
              ),
            ),
          ),
          const SizedBox(width: 10),

           Expanded(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "XP",
                  style: AppTypography.body(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    color: Colors.white54,
                    letterSpacing: 1,
                  ),
                ),
                const SizedBox(height: 3),
                ClipRRect(
                  borderRadius: BorderRadius.circular(6),
                  child: SizedBox(
                    height: 10,
                    child: Stack(
                      children: [
                        Container(color: Colors.black26),
                        TweenAnimationBuilder<double>(
                          tween: Tween(begin: 0, end: 0.3),
                          duration: const Duration(milliseconds: 600),
                          curve: Curves.easeOutCubic,
                          builder: (context, value, _) => FractionallySizedBox(
                            alignment: Alignment.centerLeft,
                            widthFactor: value,
                            child: Container(color: AppColors.success),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

              ],
            ),
          ),
          const SizedBox(width: 14),

          // --- Pièces ---
          const CartoonIcon(assetPath : AppIcons.coin, size: 26), // TODO: icône finale
          const SizedBox(width: 4),
          Text(
            "${player.coins}",
            style: AppTypography.body(fontSize: 15, fontWeight: FontWeight.w800),
          ),
          const SizedBox(width: 12),

          // --- Gemmes ---
          const CartoonIcon(assetPath: AppIcons.gem, size: 26), // TODO: icône finale
          const SizedBox(width: 4),
          Text(
            "${player.gems}",
            style: AppTypography.body(fontSize: 15, fontWeight: FontWeight.w800),
          ),
        ],
      ),
    );
  }
}
