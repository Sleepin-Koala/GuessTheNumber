import 'package:flutter/material.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_typography.dart';



class AttemptsCountdown extends StatelessWidget {
  final int attemptLeft;
  const AttemptsCountdown({super.key, required this.attemptLeft});

  @override
  Widget build(BuildContext context) {
    final isCritical = attemptLeft <= 1;
    return TweenAnimationBuilder<double>(
      key: ValueKey(attemptLeft), // rejoue le "pop" à chaque essai raté
      tween: Tween(begin: 1.3, end: 1.0),
      duration: const Duration(milliseconds: 300),
      curve: Curves.elasticOut,
      builder: (context, scale, child) => Transform.scale(scale: scale, child: child),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: isCritical ? AppColors.danger : AppColors.cardBg,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: Colors.black, width: 2.5),
        ),
        child: Text(
          "$attemptLeft ESSAI${attemptLeft > 1 ? 'S' : ''}",
          style: AppTypography.body(
            fontSize: 14,
            fontWeight: FontWeight.w800,
            color: Colors.white,
          ),
        ),
      ),
    );
  }
}
