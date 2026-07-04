
import "package:app/data/models/GameSession.dart";
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
class GameInProgress extends GameState {
  final GameSession session;
  final String? feedbackMessage;
  final double? lastDistance;
  const GameInProgress({required this.session , this.feedbackMessage , this.lastDistance});
}

@immutable
class GameFailure extends GameState {
  final String reason;

  const GameFailure({required this.reason});
}

@immutable
class GameSuccess extends GameState {

  final int finalAttemptsUsed;

  const GameSuccess({required this.finalAttemptsUsed});
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
  const GameMenu({required  this.player});
}

@immutable
class GameSelection extends GameState {
  final Player player;
  const GameSelection({required  this.player});
}

@immutable
class GameDiscovery extends GameState {
  final Player player;
  const GameDiscovery({required this.player});
}



