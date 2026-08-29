import "package:app/data/models/duel_room.dart";
import "package:app/data/models/endless_mode.dart";
import "package:app/data/models/solo_mode.dart";
import "package:app/data/models/discovery_mode_session.dart";

import "package:flutter/foundation.dart";
import "package:flutter/material.dart";
import '../../../data/models/player.dart';

class GameState {
  const GameState();
}

@immutable
class GameInitial extends GameState {
  final Player? player;
  const GameInitial({required this.player});
}

@immutable
class GameFailure extends GameState {
  final String reason;

  const GameFailure({required this.reason});
}

@immutable
class GameLoading extends GameState {
  const GameLoading();
}

@immutable
class GameError extends GameState {
  final String errorMessage;

  const GameError({required this.errorMessage});
}

@immutable
class GameMenu extends GameState {
  final Player player;
  const GameMenu({required this.player});
}

@immutable
class GameDiscovery extends GameState {
  final Player player;
  const GameDiscovery({required this.player});
}

@immutable
class GameOptions extends GameState {
  const GameOptions();
}

//solo
class ClassicState extends GameState {
  const ClassicState();
}

@immutable
class LevelSelectionState extends ClassicState {
  final Player player;
  const LevelSelectionState({required this.player});
}

@immutable
class GameClassicStart extends ClassicState {
  final SoloModeSession session;
  final String? feedbackMessage;
  final double? lastDistance;
  const GameClassicStart({
    required this.session,
    this.feedbackMessage,
    this.lastDistance,
  });
}

@immutable
class GameClassicWin extends ClassicState {
  final int currentLevel;
  final int finalAttemptsUsed;
  final int coinsEarned;
  final int xpWinned;
  final int starsWinned;

  const GameClassicWin({
    required this.finalAttemptsUsed,
    required this.currentLevel,
    required this.coinsEarned,
    required this.xpWinned,
    required this.starsWinned,
  });
}

@immutable
class GameClassicLose extends ClassicState {
  const GameClassicLose();
}

// discovery

@immutable
class DiscoverState extends GameState {
  const DiscoverState();
}

@immutable
class GameDiscoveryStart extends DiscoverState {
  final DiscoveryModeSession session;
  final String? feedbackMessage;
  final double? lastDistance;
  const GameDiscoveryStart({
    required this.session,
    this.feedbackMessage,
    this.lastDistance,
  });
}

@immutable
class GameDiscoveryWin extends DiscoverState {
  final int attempts;
  const GameDiscoveryWin({required this.attempts});
}

// endless

@immutable
class EndlessState extends GameState {
  const EndlessState();
}

@immutable
class GameEndlessStart extends EndlessState {
  final Player player;
  const GameEndlessStart({required this.player});
}

@immutable
class GameEndlessRun extends EndlessState {
  final EndlessModeSession session;
  final String? feedbackMessage;
  final double? lastDistance;
  const GameEndlessRun({
    required this.session,
    required this.feedbackMessage,
    required this.lastDistance,
  });
}

@immutable
class GameEndlessLose extends EndlessState {
  final int currentStage;
  final int bet;
  const GameEndlessLose({required this.currentStage, required this.bet});
}

@immutable
class GameEndlessWin extends EndlessState {
  final int currentStage;
  final int reward;
  const GameEndlessWin({required this.currentStage, required this.reward});
}

// MultiplayerState

@immutable
class GameDuel extends GameState {
  const GameDuel();
}

@immutable
class GameDuelSelectVariant extends GameDuel {
  const GameDuelSelectVariant();
}

@immutable
class GameDuelLobby extends GameDuel {
  final Player player;
  final List<DuelRoom> rooms;
  const GameDuelLobby({required this.player, required this.rooms});
}

@immutable
class GameDuelRoom extends GameDuel {
  final DuelRoom room;
  final Player player;
  const GameDuelRoom({required this.room, required this.player});
}

@immutable
class GameDuelStartRun extends GameDuel {
  const GameDuelStartRun();
}
