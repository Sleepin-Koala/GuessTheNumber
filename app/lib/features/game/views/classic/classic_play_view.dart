import 'dart:async';
import 'package:app/core/services/haptic_service.dart';
import 'package:app/core/widgets/GameKeyboard.dart';
import 'package:app/core/widgets/Gamepanel.dart';
import 'package:app/core/widgets/TimerBar.dart';
import 'package:app/core/widgets/animated_lives_counter.dart';
import 'package:app/features/game/bloc/game_cubit.dart';
import 'package:app/features/game/bloc/game_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:lucide_icons/lucide_icons.dart';

class ClassicPlayView extends StatefulWidget {
  final GameClassicStart state;
  const ClassicPlayView({super.key, required this.state});

  @override
  State<ClassicPlayView> createState() => _ClassicPlayViewState();
}

class _ClassicPlayViewState extends State<ClassicPlayView> {
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
  void didUpdateWidget(covariant ClassicPlayView oldWidget) {
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
                  onPressed: () => { context.read<GameCubit>().onLevelSelection(),},
                ),

                  AnimatedLivesCounter(maxLives: session.maxAttempt,remainingLives: session.attemptLeft)
               
                
              ],
            ),

            const SizedBox(height: 5),
            
            TimerBar(maxTime: session.timeLimit,),

            Expanded(
              child: Gamepanel(
                currentText: _currentInput,
                isGauge: _showGauge,
                feedbackMessage: widget.state.feedbackMessage,
                lastDistance: widget.state.lastDistance,
                max_range: session.maxRange,
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
