import 'package:app/features/game/bloc/game_cubit.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/game_state.dart';
import './home_view.dart';
import './loading_view.dart';
import './playing_view.dart';
import './result_view.dart';
import './menu_view.dart';
import './discovery_view.dart';
import './levelselection_view.dart';
import "../../../core/widgets/animated_background.dart";

class GameScreen extends StatelessWidget {
  const GameScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          const Positioned.fill(child: AnimatedGameBackground()),
          SafeArea(
            child: BlocBuilder<GameCubit, GameState>(
              builder: (context, state) {
                return switch (state) {
                  GameInitial() => const HomeView(),
                  GameMenu() => const MenuView(),
                  GameSelection() => LevelSelectionView(),
                  GameLoading() => const LoadingView(),
                  GameInProgress() => PlayingView(state: state),
                  GameDiscovery() => DiscoveryView(),
                  GameSuccess() => ResultView(
                    isWin: true,
                    attempts: state.finalAttemptsUsed,
                  ),
                  GameFailure() => ResultView(isWin: false, reason: state.reason),
                  GameError() => Center(
                    child: Text(
                      'Erreur : ${state.errorMessage}',
                      style: const TextStyle(color: Colors.red),
                    ),
                  ),
                  GameState() => throw UnimplementedError(),
                };
              },
            ),
          ),
        ],
      ),
    );
  }
}
