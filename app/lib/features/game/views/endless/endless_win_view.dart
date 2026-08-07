import 'package:app/core/widgets/CartoonButton.dart';
import 'package:app/features/game/bloc/game_cubit.dart';
import 'package:app/features/game/bloc/game_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/theme/app_typography.dart';
import '../../../../core/theme/app_icon.dart';
import '../../../../core/theme/app_colors.dart';

import '../../../../core/widgets/CartoonIcon.dart';

class EndlessWinView extends StatefulWidget {
  const EndlessWinView({super.key});

  @override
  State<EndlessWinView> createState() => _EndlessWinViewState();
}

class _EndlessWinViewState extends State<EndlessWinView> {

  @override
  Widget build(BuildContext context) {
    final currentState = context.read<GameCubit>().state as GameEndlessWin;
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            "MANCHE ${currentState.currentStage} RÉUSSIE !",
            textAlign: TextAlign.center,
            style: AppTypography.display(
              fontSize: 26,
              color: AppColors.success,
            ),
          ),
          const SizedBox(height: 24),

          const CartoonIcon(AppIcons.coin, size: 64),
          const SizedBox(height: 8),

          _CountUpNumber(target: currentState.reward),
          Text(
            "PIÈCES EN JEU",
            style: AppTypography.body(
              fontSize: 12,
              color: Colors.white54,
              letterSpacing: 2,
            ),
          ),

          const SizedBox(height: 40),

          Text(
            "Continue et affronte la manche ${currentState.currentStage+1} — mais si tu "
            "rates, tu perds TOUT ce qui est en jeu.",
            textAlign: TextAlign.center,
            style: AppTypography.body(fontSize: 18, color: Colors.white70),
          ),

          const Spacer(),

          CartoonButton(
            color: AppColors.success,
            shadowColor: const Color(0xFF1B5E20),
            onPressed: () => {context.read<GameCubit>().onMenu()},
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CartoonIcon(AppIcons.check),
                SizedBox(width: 10),
                Text("ENCAISSER ${currentState.reward} PIÈCES"),
              ],
            ),
          ),
          const SizedBox(height: 14),

          CartoonButton(
            color: const Color(0xFFFB923C),
            shadowColor: const Color(0xFF9A3412),
            onPressed: () => {context.read<GameCubit>().continueEndlessGame(currentState.reward , currentState.currentStage+1)},
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CartoonIcon(AppIcons.play),
                SizedBox(width: 10),
                Text("CONTINUER →"),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _CountUpNumber extends StatelessWidget {
  final int target;
  const _CountUpNumber({required this.target});

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<int>(
      tween: IntTween(begin: 0, end: target),
      duration: Duration(milliseconds: 300),
      builder: (context, value, child) {
        return Text(
          "$value",
          style: AppTypography.display(fontSize: 48, color: AppColors.primary),
        );
      },
    );
  }
}

class _DecisionButton extends StatefulWidget {
  final String label;
  final String icon;
  final Color color;
  final Color shadowColor;
  final VoidCallback onTap;

  const _DecisionButton({
    required this.label,
    required this.icon,
    required this.color,
    required this.shadowColor,
    required this.onTap,
  });

  @override
  State<_DecisionButton> createState() => _DecisionButtonState();
}

class _DecisionButtonState extends State<_DecisionButton> {
  bool _isPressed = false;

  @override
  Widget build(BuildContext context) {
    const double shadowHeight = 6;
    return GestureDetector(
      onTapDown: (_) => setState(() => _isPressed = true),
      onTapUp: (_) {
        setState(() => _isPressed = false);
        widget.onTap();
      },
      onTapCancel: () => setState(() => _isPressed = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 60),
        width: double.infinity,
        margin: EdgeInsets.only(top: _isPressed ? shadowHeight : 0),
        padding: const EdgeInsets.symmetric(vertical: 18),
        decoration: BoxDecoration(
          color: widget.color,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: Colors.black, width: 3),
          boxShadow: _isPressed
              ? []
              : [
                  BoxShadow(
                    color: widget.shadowColor,
                    offset: const Offset(0, shadowHeight),
                    blurRadius: 0,
                  ),
                ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CartoonIcon(widget.icon, size: 24),
            const SizedBox(width: 10),
            Text(
              widget.label,
              style: AppTypography.body(
                fontSize: 17,
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
