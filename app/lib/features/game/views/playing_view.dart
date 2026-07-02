import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/game_cubit.dart';
import '../bloc/game_state.dart';
import "../../../core/theme/app_colors.dart";
import 'package:lucide_icons/lucide_icons.dart';
import '../../../core/widgets/GameKeyboard.dart';
import "./widgets/shaking_text.dart";
import "./widgets/heat_gauge.dart";
import "./widgets/animated_lives_counter.dart";
import '../../../core/services/haptic_service.dart';
import '../../../core/theme/app_typography.dart';

class PlayingView extends StatefulWidget {
  final GameInProgress state;
  const PlayingView({super.key, required this.state});

  @override
  State<PlayingView> createState() => _PlayingViewState();
}

class _PlayingViewState extends State<PlayingView> {
  String _currentInput = "";
  bool _showGauge = false;
  Timer? _gaugeTimer;

  void _handleKeyTap(String key) {
    HapticService.triggerKeyTap();
    setState(() {
      _currentInput += key;
    });
  }

  void _handleDelete() {
    if (_currentInput.isEmpty) return;
    setState(() {
      _currentInput = _currentInput.substring(0, _currentInput.length - 1);
    });
  }

  void _handleSubmit() {
    if (_currentInput.isEmpty) return;
    final parsedNumber = int.tryParse(_currentInput);
    if (parsedNumber != null) {
      context.read<GameCubit>().makeGuess(parsedNumber);
      setState(() {
        _currentInput = "";
      });
    }
  }

  double _computeProximity(double? distance, int maxRange) {
    if (distance == null || maxRange <= 0) return 0.0;
    final normalized = 1 - (distance / maxRange);
    return normalized.clamp(0.0, 1.0);
  }

  @override
  void didUpdateWidget(covariant PlayingView oldWidget) {
    super.didUpdateWidget(oldWidget);
    final oldDistance = oldWidget.state.lastDistance;
    final newDistance = widget.state.lastDistance;

    if (oldDistance != newDistance && newDistance != null) {
      setState(() {
        _showGauge = true;
      });

      _gaugeTimer?.cancel();
      _gaugeTimer = Timer(const Duration(seconds: 2), () {
        if (mounted) {
          setState(() {
            _showGauge = false;
          });
        }
      });
    }
  }

  @override
  void dispose() {
    _gaugeTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final session = widget.state.session;

    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              IconButton(
                icon: const Icon(LucideIcons.x, color: Colors.white, size: 28),
                onPressed: () => {context.read<GameCubit>().onLevelSelection()},
              ),

              AnimatedLivesCounter(
                maxLives: session.maxAttempt,
                remainingLives: session.attemptLeft,
              ),
            ],
          ),

          const SizedBox(height: 20),

          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: AppColors.cardBg,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: Colors.black, width: 3),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    _currentInput.isEmpty ? "?" : _currentInput,
                    style: AppTypography.body(fontSize: 64 , fontWeight: FontWeight.w900,color: _currentInput.isEmpty
                          ? Colors.white24
                          : AppColors.primary,
                    )), 
                                 
                  const SizedBox(height: 16),

                  if (_showGauge) ...[
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 32),
                      child: HeatGauge(
                        proximity: _computeProximity(
                          widget.state.lastDistance,
                          session.maxRange,
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],

                  ShakingText(
                    text:
                        widget.state.feedbackMessage ??
                        "Devine le nombre entre 1 et ${session.maxRange} !",
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 24),

          GameKeyboard(
            onKeyTap: _handleKeyTap,
            onDeleteTap: _handleDelete,
            onSubmitTap: _handleSubmit,
          ),
        ],
      ),
    );
  }
}
