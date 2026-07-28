import 'package:app/features/game/bloc/game_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/CartoonButton.dart';
import '../bloc/game_cubit.dart';
import '../../../core/theme/app_typography.dart';
import '../../../core/widgets/cartoon_icon_button.dart';
import '../../../core/widgets/progress_banner.dart';
import '../../../core/widgets/CartoonIcon.dart';
import '../../../core/theme/app_icon.dart';

class HomeView extends StatelessWidget {
  const HomeView({super.key});

  @override
  Widget build(BuildContext context) {
    final currentState = context.read<GameCubit>().state;
    if (currentState is! GameInitial) return const SizedBox.shrink();
    final player = currentState.player; 


    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
    
          PlayerProgressBanner(player: player!),
    
          const Spacer(flex: 2),
          const _GameLogo(),
          const Spacer(flex: 3),
    
          CartoonButton(
            height: 76,
            onPressed: () {
              context.read<GameCubit>().onMenu();
            },
            color: AppColors.primary,
            shadowColor: AppColors.secondary,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const CartoonIcon(AppIcons.play, size: 32),
                const SizedBox(width: 14),
                Text(
                  "JOUER",
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1,
                  ),
                ),
              ],
            ),
          ),
    
          const SizedBox(height: 20),
    
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CartoonIconButton(
                child: const CartoonIcon(AppIcons.settings, size: 24),
                onPressed: () {
                  context.read<GameCubit>().onGameOptions();
                },
              ),
              const SizedBox(width: 16),                
              
              const SizedBox(width: 16),
              CartoonIconButton(
                color: AppColors.danger,
                shadowColor: const Color.fromARGB(255, 210, 41, 75),
                child: const CartoonIcon(AppIcons.logout, size: 24),
                onPressed: () {
                  SystemNavigator.pop();
                },
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _GameLogo extends StatelessWidget {
  const _GameLogo();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ShaderMask(
          shaderCallback: (bounds) => const LinearGradient(
            colors: [Colors.white, Color(0xFFE0E0FF)],
          ).createShader(bounds),
          child: Text(
            'GUESS',
            style: AppTypography.display(color: Colors.white, fontSize: 40),
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 2),
          decoration: BoxDecoration(
            color: const Color(0xFF312880),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            'THE',
            style: AppTypography.display(color: Colors.white70, fontSize: 16),
          ),
        ),
        ShaderMask(
          shaderCallback: (bounds) => const LinearGradient(
            colors: [Color(0xFFF5A623), Color(0xFFFFD700)],
          ).createShader(bounds),
          child: Text(
            'NUMBER',
            style: AppTypography.display(color: Colors.white, fontSize: 46),
          ),
        ),
      ],
    );
  }
}
