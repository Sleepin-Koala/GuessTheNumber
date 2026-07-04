import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/game_cubit.dart';
import '../bloc/game_state.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../../../core/widgets/GameKeyboard.dart';
import "./widgets/animated_lives_counter.dart";
import '../../../core/services/haptic_service.dart';
import '../../../core/widgets/Gamepanel.dart';
import '../../../core/widgets/TimerBar.dart';

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
    final isDiscovertMode = (session.maxAttempt == -1);

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
                    isDiscovertMode ?  context.read<GameCubit>().onDiscoveryPage() : context.read<GameCubit>().onLevelSelection(),
                  },
                ),

                if (!isDiscovertMode) 
                  AnimatedLivesCounter(maxLives: session.maxAttempt,remainingLives: session.attemptLeft)
                else 
                  const SizedBox.shrink()
                
              ],
            ),

            const SizedBox(height: 5),
            
            if (!isDiscovertMode) TimerBar(maxTime: session.timeLimit,),

            Expanded(
              child: Gamepanel(
                currentText: _currentInput,
                isGauge: _showGauge,
                state: widget.state,
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
