


import 'package:app/core/services/haptic_service.dart';
import 'package:app/core/theme/app_colors.dart';
import 'package:app/core/theme/app_icon.dart';
import 'package:app/core/theme/app_typography.dart';
import 'package:app/core/widgets/CartoonButton.dart';
import 'package:app/core/widgets/CartoonIcon.dart';
import 'package:app/core/widgets/GameKeyboard.dart';
import 'package:app/core/widgets/heat_gauge.dart';
import 'package:app/data/models/duel_room.dart';
import 'package:app/features/game/bloc/game_cubit.dart';
import 'package:app/features/game/bloc/game_state.dart';
import 'package:app/features/game/views/duel/duel_finished_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

class DuelRoomView extends StatefulWidget {
  const DuelRoomView({super.key});

  @override
  State<DuelRoomView> createState() => _DuelRoomViewState();
}

class _DuelRoomViewState extends State<DuelRoomView> {
    String _currentInput = "";

  void _handleKeyTap(String key) {
    HapticService.triggerKeyTap();
    if (_currentInput.length < 4) setState(() => _currentInput += key);
  }

  void _handleDelete() {
    HapticService.triggerKeyTap();
    if (_currentInput.isNotEmpty) {
      setState(() => _currentInput = _currentInput.substring(0, _currentInput.length - 1));
    }
  }

  void _handleSubmitGuess() {
    final n = int.tryParse(_currentInput);
    if (n == null) return;
    context.read<GameCubit>().submitDuelGuess(n);
    setState(() => _currentInput = "");
  }

  void _handleSubmitHide() {
    final n = int.tryParse(_currentInput);
    if (n == null) return;
    context.read<GameCubit>().submitHiddenNumber(n);
    setState(() => _currentInput = "");
  }

  @override
  Widget build(BuildContext context) {
    final currentState = context.read<GameCubit>().state;
    if (currentState is! GameDuelRoom) return SizedBox.shrink(); 
    final myId = currentState.player.id;

    final room = currentState.room;

    switch (room.status) {
      case DuelStatus.waiting:
        return _WaitingForOpponent(room: room);

      case DuelStatus.round1Hide:
      case DuelStatus.round2Hide:
        if (room.currentHiderId == myId) {
          return _HidingScreen(
            room: room,
            input: _currentInput,
            onKeyTap: _handleKeyTap,
            onDelete: _handleDelete,
            onSubmit: _handleSubmitHide,
          );
        }
        return _OpponentActionWaiting(message: "joueur 2 cache son nombre...");

        
      case DuelStatus.round1Guess:
      case DuelStatus.round2Guess:
        if (room.currentGuesserId == myId) {
          return _GuessingScreen(
            room: room,
            input: _currentInput,
            onKeyTap: _handleKeyTap,
            onDelete: _handleDelete,
            onSubmit: _handleSubmitGuess,
          );
        }
        return _OpponentActionWaiting(
          message: "test2 essaie de deviner...",
        );



      case DuelStatus.finished:
        final iWon = room.winnerId == myId;
        return DuelFinishedView(room: room, iWon: iWon, myId: myId);
    }

  }
}

class _WaitingForOpponent extends StatelessWidget {
  final DuelRoom room;
  const _WaitingForOpponent({required this.room});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text("EN ATTENTE D'UN ADVERSAIRE", textAlign: TextAlign.center, style: AppTypography.display(fontSize: 22)),
        const SizedBox(height: 12),
        Text(
          "Mise : ${room.betAmount} pièces  •  Plage 1-${room.MaxRange}",
          style: AppTypography.body(color: Colors.white54),
        ),
        const Spacer(),
        CartoonButton(
          onPressed: () => {context.read<GameCubit>().leaveDuelRoom()},
          color: AppColors.danger,
          shadowColor: const Color(0xFFB71C1C),
          child: const Text("ANNULER", style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
        ),
      ],
    );
  }
}


class _HidingScreen extends StatelessWidget {
  final DuelRoom room;
  final String input;
  final void Function(String) onKeyTap;
  final VoidCallback onDelete;
  final VoidCallback onSubmit;

  const _HidingScreen({
    required this.room,
    required this.input,
    required this.onKeyTap,
    required this.onDelete,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        children: [
          Text("CACHE TON NOMBRE", style: AppTypography.display(fontSize: 24)),
          Text(
            "Choisis un nombre entre 1 et 20 — l'adversaire va essayer de le trouver.",
            textAlign: TextAlign.center,
            style: AppTypography.body(fontSize: 13, color: Colors.white54),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: Container(
              width: double.infinity,
              decoration: BoxDecoration(
                color: AppColors.cardBg,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: Colors.black, width: 3),
              ),
              child: Center(
                child: Text(
                  input.isEmpty ? "?" : input,
                  style: AppTypography.display(
                    fontSize: 64,
                    color: input.isEmpty ? Colors.white24 : AppColors.secondary,
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),
          GameKeyboard(onKeyTap: onKeyTap, onDeleteTap: onDelete, onSubmitTap: onSubmit),
        ],
      ),
    );
  }
}

class _OpponentActionWaiting extends StatelessWidget {
  final String message;
  const _OpponentActionWaiting({required this.message});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const _PulsingDot(),
          const SizedBox(height: 24),
          Text(message, textAlign: TextAlign.center, style: AppTypography.body(fontSize: 18, fontWeight: FontWeight.w700)),
          ],
      ),
    );
  }
}

class _GuessingScreen extends StatelessWidget {
  final DuelRoom room;
  final String input;
  final void Function(String) onKeyTap;
  final VoidCallback onDelete;
  final VoidCallback onSubmit;

  const _GuessingScreen({
    required this.room,
    required this.input,
    required this.onKeyTap,
    required this.onDelete,
    required this.onSubmit,
  });

  double _computeProximity(double? distance, int maxRange) {
    if (distance == null || maxRange <= 0) return 0.0;
    final normalized = 1 - (distance / maxRange);
    return normalized.clamp(0.0, 1.0);
  }

  @override
  Widget build(BuildContext context) {
    final feedbackText = switch (room.lastFeedback) {
      "PLUS" => "C'est plus grand !",
      "MOINS" => "C'est plus petit !",
      _ => "Trouve le nombre de l'adversaire !",
    };

    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                decoration: BoxDecoration(
                  color: AppColors.cardBg,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: Colors.black, width: 2.5),
                ),
                child: Row(
                  children: [
                    const CartoonIcon(AppIcons.coin, size: 18),
                    const SizedBox(width: 6),
                    Text("${room.betAmount} en jeu", style: AppTypography.body(fontSize: 13, fontWeight: FontWeight.w800)),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.cardBg,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: Colors.black, width: 3),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    input.isEmpty ? "?" : input,
                    style: AppTypography.display(fontSize: 64, color: input.isEmpty ? Colors.white24 : AppColors.primary),
                  ),
                  const SizedBox(height: 16),
                  if (room.lastDistance != null) ...[
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 24),
                      child: HeatGauge(proximity: _computeProximity(room.lastDistance, 30)),
                    ),
                    const SizedBox(height: 16),
                  ],
                  Text(feedbackText, style: AppTypography.body(fontSize: 18, fontWeight: FontWeight.w800), textAlign: TextAlign.center),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          GameKeyboard(onKeyTap: onKeyTap, onDeleteTap: onDelete, onSubmitTap: onSubmit),
        ],
      ),
    );
  }
}

class _PulsingDot extends StatefulWidget {
  const _PulsingDot();
  @override
  State<_PulsingDot> createState() => _PulsingDotState();
}

class _PulsingDotState extends State<_PulsingDot> with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, duration: const Duration(milliseconds: 900))..repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        final scale = 0.8 + _controller.value * 0.4;
        return Transform.scale(
          scale: scale,
          child: Container(
            width: 24,
            height: 24,
            decoration: BoxDecoration(color: AppColors.secondary, shape: BoxShape.circle),
          ),
        );
      },
    );
  }
}


