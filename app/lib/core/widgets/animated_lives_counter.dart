import 'dart:async';

import 'package:app/core/theme/app_colors.dart';
import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../services/haptic_service.dart';

class AnimatedLivesCounter extends StatefulWidget {
  final int remainingLives;
  final int maxLives;

  const AnimatedLivesCounter({
    super.key,    required this.remainingLives,
    required this.maxLives,
  });

  @override
  State<AnimatedLivesCounter> createState() => _AnimatedLivesCounterState();
}

class _AnimatedLivesCounterState extends State<AnimatedLivesCounter> {
  double _scale = 1.0;
  Color _borderColor = Colors.black;
  Color _iconColor = AppColors.danger;
  Timer? _resetTimer;


  @override
  void didUpdateWidget(covariant AnimatedLivesCounter oldWidget) {
    super.didUpdateWidget(oldWidget);

    _resetTimer?.cancel();

    if (widget.remainingLives < oldWidget.remainingLives) {
      HapticService.triggerErrorImpact();
      setState(() {
        _scale = 1.3;
        _borderColor = AppColors.danger;
        _iconColor = Colors.white;
      });
    }

    if (mounted) {
      _resetTimer = Timer(const Duration(milliseconds: 200), () {
        if (mounted) {
          setState(() {
          _scale = 1.0;
          _borderColor = Colors.black;
          _iconColor = AppColors.danger;
        });

        }

      },
      );
      
    }
  }

  @override
  void dispose() {
    super.dispose();
    _resetTimer?.cancel();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedScale(
      scale: _scale,
      duration: const Duration(milliseconds: 100),
      curve: Curves.easeOutBack,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: AppColors.cardBg,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: _borderColor, width: 2),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            AnimatedColorAsIcon(icon: LucideIcons.heart, color: _iconColor),
            const SizedBox(width: 8),
            Text(
              '${widget.remainingLives} / ${widget.maxLives}',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
            ),
          ],
        ),
      ),
    );
  }
}

class AnimatedColorAsIcon extends StatelessWidget {
  final IconData icon;
  final Color color;

  const AnimatedColorAsIcon({
    super.key,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedTheme(
      data: ThemeData(iconTheme: IconThemeData(color: color)),
      duration: const Duration(milliseconds: 150),
      child: Icon(icon, size: 20),
    );
  }
}
