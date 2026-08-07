import 'dart:async';
import 'package:app/core/services/haptic_service.dart';
import 'package:app/core/theme/app_typography.dart';
import 'package:app/core/theme/app_icon.dart';
import 'package:app/core/theme/app_colors.dart';

import 'package:app/core/widgets/GameKeyboard.dart';
import 'package:app/core/widgets/Gamepanel.dart';
import 'package:app/core/widgets/animated_lives_counter.dart';

import 'package:app/features/game/bloc/game_cubit.dart';
import 'package:app/features/game/bloc/game_state.dart';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:lucide_icons/lucide_icons.dart';

import './_stateChip.dart';

class EndlessPlayView extends StatefulWidget {
  final GameEndlessRun state;
  const EndlessPlayView({super.key, required this.state});

  @override
  State<EndlessPlayView> createState() => _EndlessPlayViewState();
}

class _EndlessPlayViewState extends State<EndlessPlayView> {
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

  @override
  void didUpdateWidget(covariant EndlessPlayView oldWidget) {
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

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                IconButton(
                  icon: const Icon(
                    LucideIcons.x,
                    color: Colors.white,
                    size: 28,
                  ),
                  onPressed: () => {
                    context.read<GameCubit>().onEndlessMode(),
                  },
                ),
                Expanded(
                  child: Column(
                    children: [
                      Text(
                        "MANCHE ${(session.maxRange / 10).round()}",
                        style: AppTypography.display(fontSize: 22),
                      ),
                      Text(
                        "Cherche entre 1 et ${session.maxRange}",
                        style: AppTypography.body(
                          fontSize: 13,
                          color: Colors.white54,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 5),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,

              children: [
                StatChip(
                  icon: AppIcons.coin,
                  label: "EN JEU",
                  value: "${session.bet}",
                  color: AppColors.primary,
                ),
                AnimatedLivesCounter(
                  maxLives: session.maxAttempt,
                  remainingLives: session.attemptLeft,
                ),
              ],
            ),

            Expanded(
              child: Gamepanel(
                currentText: _currentInput,
                isGauge: _showGauge,
                max_range: session.maxRange,
                lastDistance: widget.state.lastDistance,
                feedbackMessage: widget.state.feedbackMessage,
              ),
            ),

            const SizedBox(height: 12),

            GameKeyboard(
              onKeyTap: _handleKeyTap,
              onDeleteTap: _handleDelete,
              onSubmitTap: _handleSubmit,
            ),
          ],
        ),
      ),
    );
  }
}
