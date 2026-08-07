


import 'dart:math';

import 'package:app/core/theme/app_colors.dart';
import 'package:app/core/theme/app_icon.dart';
import 'package:app/core/theme/app_typography.dart';
import 'package:app/core/widgets/CartoonButton.dart';
import 'package:app/core/widgets/CartoonIcon.dart';
import 'package:app/data/models/duel_room.dart';
import 'package:app/features/game/bloc/game_cubit.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

class DuelFinishedView extends StatefulWidget {
  final DuelRoom room;
  final bool iWon;
  final String myId;
  const DuelFinishedView({super.key, required this.room, required this.iWon, required this.myId});

  @override
  State<DuelFinishedView> createState() => DuelFinishedViewState();
}

class DuelFinishedViewState extends State<DuelFinishedView> with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, duration: const Duration(milliseconds: 500))..forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final room = widget.room;
    final resultColor = widget.iWon ? AppColors.success : AppColors.danger;

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        if (widget.iWon) return child!;
        final t = _controller.value;
        final dx = sin(t * pi * 8) * 12 * (1 - t);
        return Transform.translate(offset: Offset(dx, 0), child: child);
      },
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              widget.iWon ? "VICTOIRE !" : "DÉFAITE",
              style: AppTypography.display(fontSize: 46, color: resultColor),
            ),
            const SizedBox(height: 24),
            const CartoonIcon(AppIcons.coin, size: 56),
            const SizedBox(height: 8),
            TweenAnimationBuilder<int>(
              tween: IntTween(begin: 0, end: widget.iWon ? room.betAmount*2 : 0),
              duration: const Duration(milliseconds: 900),
              curve: Curves.easeOutCubic,
              builder: (context, value, _) => Text(
                widget.iWon ? "+$value" : "-${room.betAmount}",
                style: AppTypography.display(fontSize: 40, color: resultColor),
              ),
            ),
            const SizedBox(height: 32),
            _AttemptsSummary(room: room, myId: widget.myId),
            const Spacer(),
            CartoonButton(
              onPressed: () => context.read<GameCubit>().resetToHome(),
              color: AppColors.primary,
              shadowColor: AppColors.secondary,
              child: const Text("RETOUR AU MENU", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }
}


class _AttemptsSummary extends StatelessWidget {
  final DuelRoom room;
  final String myId;
  const _AttemptsSummary({required this.room, required this.myId});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.black, width: 3),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          Column(
            children: [
              Text("MANCHE 1", style: AppTypography.body(fontSize: 10, color: Colors.white54)),
              Text("${room.round1AttemptsUsed ?? '-'}", style: AppTypography.display(fontSize: 22)),
            ],
          ),
          Container(width: 2, height: 32, color: Colors.white12),
          Column(
            children: [
              Text("MANCHE 2", style: AppTypography.body(fontSize: 10, color: Colors.white54)),
              Text("${room.round2AttemptsUsed ?? '-'}", style: AppTypography.display(fontSize: 22)),
            ],
          ),
        ],
      ),
    );
  }
}
