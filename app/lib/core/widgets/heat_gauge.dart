import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';

class HeatGauge extends StatelessWidget {
  final double proximity;
  const HeatGauge({super.key, required this.proximity});

  Color _colorForProximity(double t) {
    if (t < 0.5) {
      return Color.lerp(
        const Color(0xFF4FACFE), // froid (bleu)
        const Color(0xFFFB923C), // tiède (orange)
        t / 0.5,
      )!;
    } else {
      return Color.lerp(
        const Color(0xFFFB923C), // tiède (orange)
        AppColors.danger, // brûlant (rouge)
        (t - 0.5) / 0.5,
      )!;
    }
  }

  String _labelForProximity(double t) {
    if (t < 0.2) return "🥶 Glacial";
    if (t < 0.45) return "❄️ Froid";
    if (t < 0.7) return "🌤️ Tiède";
    if (t < 0.9) return "🔥 Chaud";
    return "🌋 Brûlant !";
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          height: 12,
          width: double.infinity,
          child: TweenAnimationBuilder<double>(
            tween: Tween<double>(begin: 0, end: proximity.clamp(0.0, 1.0)),
            duration: const Duration(milliseconds: 500),
            curve: Curves.easeOutCubic,
            builder: (context, animatedValue, child) {
              return Stack(
                children: [
                  Container(
                    width: double.infinity,
                    height: double.infinity,
                    decoration: BoxDecoration(
                      color: AppColors.cardBg,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.black, width: 3),
                    ),
                  ),

                  Align(
                    alignment: Alignment.centerLeft,
                    child: FractionallySizedBox(
                      alignment: Alignment.centerLeft,
                      widthFactor: animatedValue,
                      heightFactor: 1.0,
                      child: Container(
                        decoration: BoxDecoration(
                          color: _colorForProximity(animatedValue),
                          borderRadius: BorderRadius.circular(9),
                        ),
                      ),
                    ),
                  ),
                ],
              );
            },
          ),
        ),

        const SizedBox(height: 8),

        Text(
          _labelForProximity(proximity),
          key: ValueKey(_labelForProximity(proximity)),
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w900,
            color: _colorForProximity(proximity),
          ),
        ),
      ],
    );
  }
}
