import 'package:app/core/widgets/Gamepanel.dart';
import 'package:app/features/game/bloc/game_cubit.dart';
import 'package:app/features/game/bloc/game_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/widgets/GameKeyboard.dart';
import '../../../../core/widgets/CartoonIcon.dart';
import '../../../../core/widgets/animated_lives_counter.dart';

import '../../../../core/theme/app_icon.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_typography.dart';

import './_stateChip.dart';

import '../../../../core/services/haptic_service.dart';

class EndlessPlayView extends StatefulWidget {
  const EndlessPlayView({super.key});

  @override
  State<EndlessPlayView> createState() => _EndlessPlayViewState();
}

class _EndlessPlayViewState extends State<EndlessPlayView> {
  String _currentInput = "";

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
  Widget build(BuildContext context) {
    final currentState = context.read<GameCubit>().state;
    if (currentState is! GameEndlessRun) return SizedBox.shrink();
    final currentSession = currentState.session;

    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        children: [
          Row(
            children: [
              IconButton(
                icon: const CartoonIcon(AppIcons.close, size: 26),
                onPressed: () => context.read<GameCubit>().resetToHome(),
              ),

              Expanded(
                child: Column(
                  children: [
                    Text(
                      "MANCHE ${(currentSession.maxRange / 10).round()}",
                      style: AppTypography.display(fontSize: 22),
                    ),
                    Text(
                      "Cherche entre 1 et ${currentSession.maxRange}",
                      style: AppTypography.body(
                        fontSize: 13,
                        color: Colors.white54,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 48),
            ],
          ),
          const SizedBox(height: 12),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,

            children: [
              StatChip(
                icon: AppIcons.coin,
                label: "EN JEU",
                value: "${currentSession.bet}",
                color: AppColors.primary,
              ),
              AnimatedLivesCounter(
                maxLives: currentSession.maxAttempt,
                remainingLives: currentSession.attemptLeft,
              ),
            ],
          ),
          const SizedBox(height: 12),

          Gamepanel(
            currentText: _currentInput,
            lastDistance: currentState.lastDistance,
            max_range: currentSession.maxRange, 
            isGauge: false,
            feedbackMessage: currentState.feedbackMessage,
          ),
          const SizedBox(height: 12),

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
