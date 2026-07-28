import 'package:app/features/game/bloc/game_cubit.dart';
import 'package:app/features/game/views/classic/classic_play_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/game_state.dart';

import './home_view.dart';
import './loading_view.dart';
import './result_view.dart';
import './menu_view.dart';
import './options_view.dart';

import 'classic/levelselection_view.dart';

//endless
import './endless/endless_view.dart';
import './endless/endless_start_view.dart';
import 'endless/endless_lose_view.dart';
import 'endless/endless_win_view.dart';

//discovery
import './discovery/d_result_view.dart';
import 'discovery/discovery_view.dart';
import './discovery/discovery_play_view.dart';





import "../../../core/widgets/animated_background.dart";


class GameScreen extends StatelessWidget {
  const GameScreen({super.key});

  bool _handleBackNavigation(BuildContext context, GameState state) {
    final cubit = context.read<GameCubit>();

    switch (state) {
      case GameInitial():
        return true; 

      case GameLoading():
        return false; 

      case GameMenu():
        cubit.resetToHome();
        return false;

      case LevelSelectionState():
      case GameDiscovery():
        cubit.onMenu();
        return false;

      case GameOptions():
        cubit.resetToHome();
        return false;

      case LevelSelectionState():
        cubit.abandonGame();
        return false;

      case GameSuccess():
      case GameFailure():
        cubit.resetToHome();
        return false;

      case GameError():
        return true; 

      default:
        return true;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          const Positioned.fill(child: AnimatedGameBackground()),
          SafeArea(
            child: BlocBuilder<GameCubit, GameState>(
              builder: (context, state) {
                return PopScope(
                  canPop: false,
                  onPopInvokedWithResult: (didPop, result) {
                    if (didPop) return;
                    final shouldLetSystemHandle = _handleBackNavigation(
                      context,
                      state,
                    );
                    if (shouldLetSystemHandle) {
                      SystemNavigator.pop();
                    }
                  },

                  child: switch (state) {
                    GameInitial() => const HomeView(),
                    GameMenu() => const MenuView(),
                    
                    //discovery
                    GameDiscovery() => DiscoveryView(),
                    GameDiscoveryStart() => DiscoveryPlayView(state: state),


                    GameOptions() => OptionsView(),
                    GameSuccess() => ResultView(
                      isWin: true,
                      attempts: state.finalAttemptsUsed,
                    ),
                    GameFailure() => ResultView(
                      isWin: false,
                      reason: state.reason,
                    ),
                    GameError() => Center(
                      child: Text(
                        'Erreur : ${state.errorMessage}',
                        style: const TextStyle(color: Colors.red),
                      ),
                    ),

                    // discover state
                    ResultDiscovery() => DiscoverModeWinView(
                      attempts: state.attempts,
                    ),

                    // endless state
                    GameEndlessStart() => EndlessStartView(),
                    GameEndlessRun() => EndlessPlayView(),
                    GameEndlessLose() => EndlessBustView(),
                    GameEndlessWin() => EndlessWinView(),

                    //solo
                    LevelSelectionState() => LevelSelectionView(),
                    GameClassicStart() => ClassicPlayView(state: state,),
                    



                    GameLoading() => const LoadingView(),


                    GameState() => throw UnimplementedError(),
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
