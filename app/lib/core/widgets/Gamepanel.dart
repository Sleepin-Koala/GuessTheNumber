import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_typography.dart';
import "../widgets/heat_gauge.dart";
import '../../features/game/bloc/game_state.dart';
import '../widgets/shaking_text.dart';

class Gamepanel extends StatelessWidget {
  final String currentText;
  final bool isGauge;
  final int max_range;
  final String? feedbackMessage;
  final double? lastDistance;


  const Gamepanel({super.key, required this.currentText , required this.isGauge , required this.max_range ,this.feedbackMessage,this.lastDistance});

    double _computeProximity(double? distance, int maxRange) {
    if (distance == null || maxRange <= 0) return 0.0;
    final normalized = 1 - (distance / maxRange);
    return normalized.clamp(0.0, 1.0);
  }


  @override
  Widget build(BuildContext context) {
    
    return Container(
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.black, width: 3),
      ),

      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            currentText.isEmpty ? "?" : currentText,
            style: AppTypography.body(
              fontSize: 64,
              fontWeight: FontWeight.w900,
              color: currentText.isEmpty ? Colors.white24 : AppColors.primary,
            ),
          ),

          const SizedBox(height: 16),

          if (isGauge) ...[
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 32),
                      child: HeatGauge(
                        proximity: _computeProximity(
                          lastDistance,
                          max_range,
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],
                  ShakingText(
                    text:
                        feedbackMessage ??
                        "Devine le nombre entre 1 et ${max_range} !",
                  ),
        ],
      ),

  
    );
  }
}
