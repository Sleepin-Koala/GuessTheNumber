import 'package:flutter/material.dart';

import '../theme/app_typography.dart';
import '../theme/app_colors.dart';

import '../widgets/heat_gauge.dart';


double _computeProximity(double? distance, int maxRange) {
    if (distance == null || maxRange <= 0) return 0.0;
    return (1 - (distance / maxRange)).clamp(0.0, 1.0);
  }

class GameCard extends StatelessWidget {
  final String currentInput;
  final double? lastDistance;
  final int range;
  const GameCard({super.key , required this.currentInput, required this.lastDistance,required this.range});

  @override
  Widget build(BuildContext context) {
    return Expanded(
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.cardBg.withOpacity(0.9),
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: Colors.black, width: 3),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  FittedBox(
                    fit: BoxFit.scaleDown,
                    child: Text(                    
                    currentInput.isEmpty ? "?" : currentInput,
                    style: AppTypography.display(
                      fontSize: 50,
                      color: currentInput.isEmpty ? Colors.white24 : AppColors.primary,
                    ),
                  ),
                  ),
                  

                  const SizedBox(height: 16),
                  if (lastDistance != null) ...[
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 24),
                      child: HeatGauge(proximity: _computeProximity(lastDistance, range)),
                    ),
                    const SizedBox(height: 16),
                  ],
                  Text(
                    // widget.state.feedbackMessage ??
                    "À toi de jouer !",
                    style: AppTypography.body(
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          )
;
  }
}