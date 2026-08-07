import "dart:math";

import 'package:app/features/game/bloc/game_state.dart';
import 'package:flutter/material.dart';

import '../../../../core/widgets/CartoonButton.dart';
import '../../../../core/widgets/CartoonIcon.dart';

import '../../../../core/theme/app_typography.dart';
import '../../../../core/theme/app_icon.dart';
import '../../../../core/theme/app_colors.dart';

import 'package:flutter_bloc/flutter_bloc.dart';
import '../../bloc/game_cubit.dart';


// EndlessBustView
class EndlessBustView extends StatefulWidget {
  const EndlessBustView({super.key});

  @override
  State<EndlessBustView> createState() => _EndlessBustViewState();
}
class _EndlessBustViewState extends State<EndlessBustView>
    with SingleTickerProviderStateMixin {
  late AnimationController _shakeController;

  @override
  void initState() {
    super.initState();
    _shakeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    )..forward();
  }

  @override
  void dispose() {
    _shakeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = context.read<GameCubit>().state;
    if (state is! GameEndlessLose ) return SizedBox.shrink();

    return AnimatedBuilder(
      animation: _shakeController,
      builder: (context, child) {
        final t = _shakeController.value;
        final dx = sin(t * pi * 8) * 12 * (1 - t);
        return Transform.translate(offset: Offset(dx, 0), child: child);
      },
      child: Stack(
        children: [
          AnimatedBuilder(
            animation: _shakeController,
            builder: (context, _) {
              return Positioned.fill(
                child: IgnorePointer(
                  child: Container(
                    color: AppColors.danger.withOpacity(
                      0.35 * (1 - _shakeController.value),
                    ),
                  ),
                ),
              );
            },
          ),

          Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  "PERDU",
                  textAlign: TextAlign.center,
                  style: AppTypography.display(
                    fontSize: 52,
                    color: AppColors.danger,
                  ),
                ),

                const SizedBox(height: 16),
                Text(
                  "MANCHE",
                  textAlign: TextAlign.center,
                  style: AppTypography.body(
                    fontSize: 15,
                    color: Colors.white60,
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  "${state.currentStage}",
                  textAlign: TextAlign.center,
                  style: AppTypography.display(fontSize: 40),
                ),
                const SizedBox(height: 32),

                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 14,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.cardBg,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.black, width: 3),
                  ),
                  child: Column(
                    children: [
                      Text(
                        "TU PERDS",
                        style: AppTypography.body(
                          fontSize: 11,
                          color: Colors.white54,
                          letterSpacing: 1.5,
                        ),
                      ),
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const CartoonIcon(AppIcons.coin, size: 22),
                          const SizedBox(width: 6),
                          Text(
                            "${state.bet}",
                            style: AppTypography.body(
                              fontSize: 22,
                              fontWeight: FontWeight.w800,
                              color: AppColors.danger,
                              // decoration: TextDecoration.lineThrough,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const Spacer(),
                CartoonButton(
                  onPressed: () => context.read<GameCubit>().onMenu(),
                  color: AppColors.primary,
                  shadowColor: AppColors.secondary,
                  child: const Text(
                    "RETOUR AU MENU",
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                ),

                const SizedBox(height: 12),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
