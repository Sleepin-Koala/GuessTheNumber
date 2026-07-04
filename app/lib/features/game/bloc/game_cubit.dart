import 'package:app/data/repositories/game_repository.dart';
import 'package:app/data/repositories/user_repository.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'game_state.dart';
import "../../../data/models/GuessOutCome.dart";
import "../../../data/models/GameSession.dart";
import "../../../data/models/player.dart";

class GameCubit extends Cubit<GameState> {
  final GameRepository _gameRepository;
  final UserRepository _userRepository;

  String? _sessionId;
  late int _currentLevel;
  late Player? _currentPlayer;

  GameCubit({
    required GameRepository gameRepository,
    required UserRepository userRepository,
  }) : _gameRepository = gameRepository,
       _userRepository = userRepository,
       super(GameInitial(player: null));

  void onMenu() {
    if (_currentPlayer == null) {
      emit(const GameError(errorMessage: "Profil joueur non initialisé."));
      return;
    } else {
      emit(GameMenu(player: _currentPlayer!));
    }
  }

  void onLevelSelection() {
    if (_currentPlayer == null) {
      emit(const GameError(errorMessage: "Profil joueur non initialisé."));
      return;
    } else {
      emit(GameSelection(player: _currentPlayer!));
    }
  }

  Future<void> startNewGame({required int level}) async {
    if (_currentPlayer == null) {
      emit(const GameError(errorMessage: "Profil joueur non initialisé."));
      return;
    }

    emit(const GameLoading());

    _currentLevel = level;

    try {
      final newSession = await _gameRepository.StartSoloGame(
        playerId: _currentPlayer!.id,
        level: level,
      );
      _sessionId = newSession.sessionId;

      emit(GameInProgress(session: newSession));
    } catch (e) {
      emit(GameError(errorMessage: e.toString()));
    }
  }

  void onDiscoveryPage() {
    emit(GameDiscovery(player: _currentPlayer!));
  }

  Future<void> makeGuess(int number) async {
    final currentState = state;
    if (currentState is! GameInProgress || _sessionId == null) return;

    try {
      final result = await _gameRepository.makeGuess(
        sessionId: _sessionId!,
        playerId: _currentPlayer!.id,
        number: number,
      );

      switch (result.outcome) {
        case GuessOutcome.OK:
          // Le joueur a gagné ! On calcule le nombre d'essais utilisés
          final attemptsUsed =
              currentState.session.maxAttempt - result.attemptLeft;

          // On notifie le serveur de la victoire pour mettre à jour le profil (XP, Coins)
          final res = await _gameRepository.endGameSession(
            sessionId: _sessionId!,
            playerId: _currentPlayer!.id,
            status: 'win',
            levelPlayed: _currentLevel,
          );
          _currentPlayer = res;

          emit(GameSuccess(finalAttemptsUsed: attemptsUsed));
          break;

        case GuessOutcome.PLUS:
        case GuessOutcome.MOINS:
          if (result.attemptLeft <= 0) {
            // Plus de vies : Défaite sur le serveur
            final res = await _gameRepository.endGameSession(
              sessionId: _sessionId!,
              playerId: _currentPlayer!.id,
              status: 'lose',
              levelPlayed: _currentLevel,
            );
            _currentPlayer = res;
            emit(const GameFailure(reason: "attemps"));
          } else {
            final updatedSession = GameSession(
              sessionId: currentState.session.sessionId,
              maxAttempt: currentState.session.maxAttempt,
              attemptLeft: result.attemptLeft,
              maxRange: currentState.session.maxRange,
              timeLimit: currentState.session.timeLimit,
            );

            final feedback = result.outcome == GuessOutcome.PLUS
                ? "Plus petit que $number ! 📈"
                : "Plus grand que $number ! 📉";

            emit(
              GameInProgress(
                session: updatedSession,
                feedbackMessage: feedback,
                lastDistance: result.distance,
              ),
            );
          }
          break;
      }
    } catch (e) {
      // Si une erreur réseau survient pendant le guess, on ne détruit pas la partie,
      // on peut émettre un état d'erreur ou le gérer via un feedback.
      // Pour la rigueur du jalon, on bascule en GameError.
      emit(GameError(errorMessage: e.toString()));
    }
  }

  Future<void> startDiscoveryGame({required max_range}) async {
    if (_currentPlayer == null) {
      emit(const GameError(errorMessage: "Profil joueur non initialisé."));
      return;
    }
    emit(const GameLoading());

    try {
      final discovery_session = await _gameRepository.startDiscoveryGame(
        player_id: _currentPlayer!.id,
        max_range: max_range,
      );
      _sessionId = discovery_session.sessionId;

      emit(GameInProgress(session: discovery_session));
    } catch (e) {
      emit(GameError(errorMessage: e.toString()));
    }
  }

  void onTimeUp() {
    emit(const GameFailure(reason: "time"));
  }

  Future<void> initializeApp() async {
    emit(const GameLoading());

    try {
      _currentPlayer = await _userRepository.getNewPlayer();
      emit(GameInitial(player: _currentPlayer!));
    } catch (e) {
      emit(GameError(errorMessage: "Impossible de créer votre profil : $e"));
    }
  }

  Future<void> abandonGame() async {
    if (_sessionId != null) {
      try {
        await _gameRepository.endGameSession(
          sessionId: _sessionId!,
          playerId: _currentPlayer!.id,
          status: 'abandoned',
          levelPlayed: _currentLevel,
        );
      } catch (_) {
        // Mode silencieux si l'abandon échoue par manque de réseau
      }
    }
    // emit(const GameInitial());
  }
}
