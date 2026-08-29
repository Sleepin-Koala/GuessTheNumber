import 'package:app/core/theme/app_colors.dart';
import 'package:app/core/theme/app_typography.dart';
import 'package:app/core/widgets/CartoonButton.dart';
import 'package:app/core/widgets/CartoonIcon.dart';
import 'package:app/core/widgets/CustomSVGBackground.dart';
import 'package:app/features/game/bloc/game_cubit.dart';
import 'package:app/features/game/bloc/game_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'dart:math' as math;

class ClassicWinView extends StatefulWidget {
  const ClassicWinView({super.key});

  @override
  State<ClassicWinView> createState() => _ClassicWinViewState();
}

class _ClassicWinViewState extends State<ClassicWinView>
    with TickerProviderStateMixin {
  final List<AnimationController> _controller = [];
  final List<Animation<Offset>> _animatedSlide = [];
  final List<Animation<double>> _animatedScale = [];

  @override
  void initState() {
    super.initState();
    _initAnimation();
  }

  void _initAnimation() {
    for (int i = 0; i < 3; i++) {
      final controller = AnimationController(
        duration: const Duration(milliseconds: 400),
        vsync: this,
      );

      final _slideAnim = Tween<Offset>(
        begin: const Offset(0, 1.2),
        end: i == 1 ? Offset(0, -0.4) : Offset.zero,
      ).animate(CurvedAnimation(parent: controller, curve: Curves.elasticOut));

      final _scaleAnim = Tween<double>(
        begin: 0.0,
        end: 1.0,
      ).animate(CurvedAnimation(parent: controller, curve: Curves.bounceInOut));

      _controller.add(controller);
      _animatedScale.add(_scaleAnim);
      _animatedSlide.add(_slideAnim);

      _starAnimations();
    }
  }

  void _starAnimations() {
    for (int index = 0; index < 3; index++) {
      Future.delayed(Duration(milliseconds: index * 400), () {
        if (!mounted) return;
        _controller[index].forward();
      });
    }
  }

  @override
  void dispose() {
    super.dispose();
    for (AnimationController c in _controller) {
      c.dispose();
    }
  }

  @override
  Widget build(BuildContext context) {
    final Color headerColor = AppColors.success;
    final Color shadowHeaderColor = const Color(0xFF1B5E20);
    final String title = 'VICTOIRE !';
    final IconData icon = LucideIcons.trophy;
    final state = context.read<GameCubit>().state;
    if (state is! GameClassicWin) return SizedBox.shrink();
    final attempts = state.finalAttemptsUsed;
    final coinsEarned = state.coinsEarned;
    final xpWinned = state.xpWinned;
    final starsWinned = state.starsWinned;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 40.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SizedBox(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(3, (index) => _buildWidget(index , starsWinned)),
            ),
          ),

          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: headerColor,
              borderRadius: BorderRadius.circular(32),
              border: Border.all(color: Colors.black, width: 4),
              boxShadow: [
                BoxShadow(
                  color: shadowHeaderColor,
                  offset: const Offset(0, 8),
                  blurRadius: 0,
                ),
              ],
            ),
            child: Column(
              children: [
                Icon(icon, size: 80, color: Colors.white),
                const SizedBox(height: 16),
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 36,
                    fontWeight: FontWeight.w900,
                    color: Colors.white,
                    letterSpacing: 2,
                    shadows: [
                      Shadow(
                        color: Colors.black,
                        offset: Offset(2, 2),
                        blurRadius: 0,
                      ),
                    ],
                  ),
                ),

                Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,

                  children: [
                    Container(
                      decoration: BoxDecoration(
                        color: Color.fromARGB(170, 34, 33, 33),
                        borderRadius: BorderRadius.circular(16),
                      ),

                      child: Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: Column(
                          children: [
                            Text(
                              "XP",
                              style: AppTypography.display(fontSize: 16),
                            ),
                            Text(
                              xpWinned.toString(),
                              style: AppTypography.display(
                                fontSize: 32,
                                color: Colors.yellow,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    SizedBox(height: 10),
                    Container(
                      decoration: BoxDecoration(
                        color: Color.fromARGB(170, 34, 33, 33),
                        borderRadius: BorderRadius.circular(16),
                      ),

                      child: Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: Column(
                          children: [
                            Text(
                              "pieces gagne",
                              style: AppTypography.display(fontSize: 16),
                            ),
                            Text(
                              coinsEarned.toString(),
                              style: AppTypography.display(
                                fontSize: 32,
                                color: Colors.yellow,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 40),

          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AppColors.cardBg,
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: Colors.black, width: 3),
            ),

            child: Column(
              children: [
                Text(
                  "Tu as trouvé le nombre secret !",
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 18, color: Colors.white70),
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      LucideIcons.zap,
                      color: AppColors.primary,
                      size: 24,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Essais utilisés : $attempts',
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w900,
                        color: AppColors.primary,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const Spacer(),
          Row(
            children: [
              CartoonButton(
                onPressed: () {
                  context.read<GameCubit>().onLevelSelection();
                },
                color: AppColors.primary,
                shadowColor: AppColors.secondary,
                child: Icon(LucideIcons.layers, color: Colors.white),
              ),

              CartoonButton(
                onPressed: () {
                  context.read<GameCubit>().startClassicSession(
                    level: state.currentLevel + 1,
                  );
                },
                color: AppColors.primary,
                shadowColor: AppColors.secondary,
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'NIVEAU SUIVANT',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    SizedBox(width: 12),
                    Icon(LucideIcons.moveRight, color: Colors.white),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildWidget(int index, int maxStars) {

    if (index < maxStars ) {
      return Padding(
      padding: const EdgeInsetsDirectional.all(12),
      child: SlideTransition(
        position: _animatedSlide[index],
        child: ScaleTransition(
          scale: _animatedScale[index],
          child: const CartoonIcon("assets/icons/win_star.svg", size: 80),
        ),
      ),
    );
    }
    else {
      return SizedBox.shrink();
    }
    
  }
}
