import 'package:app/data/models/endless_mode.dart';
import 'package:app/data/models/discovery_mode_session.dart';
import 'package:app/data/repositories/game_repository.dart';
import 'package:app/data/repositories/user_repository.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'game_state.dart';
import "../../../data/models/GuessOutCome.dart";
import "../../../data/models/solo_mode.dart";
import "../../../data/models/player.dart";
import '../../../core/services/settings_service.dart';

class GameData {
  final int numberDiscoverAttempt;
  final int? currentBet;
  GameData({this.numberDiscoverAttempt = 0, this.currentBet});

  GameData copyWith({int? numberDiscoverAttempt, int? currentBet}) {
    return GameData(
      numberDiscoverAttempt:
          numberDiscoverAttempt ?? this.numberDiscoverAttempt,
      currentBet: currentBet ?? this.currentBet,
    );
  }
}

class GameCubit extends Cubit<GameState> {
  final GameRepository _gameRepository;
  final UserRepository _userRepository;

  String? _sessionId;
  late int _currentLevel;
  late Player? _currentPlayer;
  GameData _gamedata = GameData();

  GameCubit({
    required GameRepository gameRepository,
    required UserRepository userRepository,
  }) : _gameRepository = gameRepository,
       _userRepository = userRepository,
       super(GameInitial(player: null));

  void resetToHome() {
    emit(GameInitial(player: _currentPlayer));
  }

  Future<void> makeGuess(int number) async {
    final currentState = state;
    if (_sessionId == null) return;

    try {
      final result = await _gameRepository.makeGuess(
        sessionId: _sessionId!,
        playerId: _currentPlayer!.id,
        number: number,
      );

      if (result.type == "discover" && currentState is GameDiscoveryStart) {
        handleGuessDiscovery(
          result: result,
          currentState: currentState,
          number: number,
        );
      }
      // ENDLESS
      else if (result.type == "endless" && currentState is GameEndlessRun) {
        handleGuessEndless(
          result: result,
          currentState: currentState,
          number: number,
        );
      } else if (result.type == "solo" && currentState is GameClassicStart) {
        handleGuessClassic(
          result: result,
          currentState: currentState,
          number: number,
        );
      }
    } catch (e) {
      emit(GameError(errorMessage: e.toString()));
    }
  }

  Future<void> initializeApp() async {
    emit(const GameLoading());

    try {
      await SettingsService.init();

      if (SettingsService.playerId == "") {
        _currentPlayer = await _userRepository.getNewPlayer();
        SettingsService.setData(_currentPlayer!.id);
      } else {
        _currentPlayer = await _userRepository.getActualPlayer(
          SettingsService.playerId);
        // _currentPlayer = await _userRepository.getNewPlayer();
        // SettingsService.setData(_currentPlayer!.id);
      }

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
      } catch (_) {}
    }
  }

  // changer
  void onEndlessMode() {
    if (_currentPlayer == null) {
      emit(const GameError(errorMessage: "Profil joueur non initialisé."));
      return;
    } else {
      emit(GameEndlessStart(player: _currentPlayer!));
    }
  }

  void onTimeUp() {
    emit(const GameFailure(reason: "time"));
  }

  void onMenu() {
    if (_currentPlayer == null) {
      emit(const GameError(errorMessage: "Profil joueur non initialisé."));
      return;
    } else {
      emit(GameMenu(player: _currentPlayer!));
    }
  }

  void onDiscoveryPage() {
    emit(GameDiscovery(player: _currentPlayer!));
  }

  void onGameOptions() {
    emit(GameOptions());
  }

  void onLevelSelection() {
    if (_currentPlayer == null) {
      emit(const GameError(errorMessage: "Profil joueur non initialisé."));
      return;
    } else {
      emit(LevelSelectionState(player: _currentPlayer!));
    }
  }

  // ENDLESS

  Future<void> startEndlessGame(bet) async {
    if (_currentPlayer == null) {
      emit(const GameError(errorMessage: "Profil joueur non initialisé."));
      return;
    }
    emit(const GameLoading());
    try {
      _gamedata = _gamedata.copyWith(currentBet: bet);

      final endlessSession = await _gameRepository.endlessMode.start(
        player_id: _currentPlayer!.id,
        bet: bet,
      );
      _sessionId = endlessSession.sessionId;
      emit(
        GameEndlessRun(
          session: endlessSession,
          feedbackMessage: null,
          lastDistance: null,
        ),
      );
    } catch (e) {
      emit(GameError(errorMessage: e.toString()));
    }
  }

  void handleGuessEndless({
    required GuessResult result,
    required GameEndlessRun currentState,
    required int number,
  }) async {
    switch (result.outcome) {
      case GuessOutcome.PLUS:
      case GuessOutcome.MOINS:
        if (result.attemptLeft == 0) {
          emit(GameEndlessLose(currentStage: currentState.session.stage));
        } else {
          _gamedata = _gamedata.copyWith(
            numberDiscoverAttempt: _gamedata.numberDiscoverAttempt + 1,
          );

          final updatedSession = EndlessModeSession(
            sessionId: currentState.session.sessionId,
            maxAttempt: currentState.session.maxAttempt,
            attemptLeft: result.attemptLeft,
            maxRange: currentState.session.maxRange,
            timeLimit: currentState.session.timeLimit,
            bet: _gamedata.currentBet!,
            winnable: 300,
            stage: currentState.session.stage,
          );

          final feedback = result.outcome == GuessOutcome.PLUS
              ? "Plus petit que $number ! 📈"
              : "Plus grand que $number ! 📉";

          emit(
            GameEndlessRun(
              session: updatedSession,
              feedbackMessage: feedback,
              lastDistance: result.distance,
            ),
          );
        }

      case GuessOutcome.OK:
        await _gameRepository.endlessMode.endGameSession(
          sessionId: _sessionId!,
          playerId: _currentPlayer!.id,
          status: 'win',
        );

        emit(GameEndlessWin(currentStage: currentState.session.stage));
    }
  }

  // CLASSIC

  Future<void> startClassicSession({required int level}) async {
    if (_currentPlayer == null) {
      emit(const GameError(errorMessage: "Profil joueur non initialisé."));
      return;
    }

    emit(const GameLoading());

    _currentLevel = level;

    try {
      final newSession = await _gameRepository.soloMode.start(
        playerId: _currentPlayer!.id,
        level: level,
      );
      _sessionId = newSession.sessionId;

      emit(GameClassicStart(session: newSession));
    } catch (e) {
      emit(GameError(errorMessage: e.toString()));
    }
  }

  void handleGuessClassic({
    required GuessResult result,
    required GameClassicStart currentState,
    required int number,
  }) async {
    switch (result.outcome) {
      case GuessOutcome.OK:
        final res = await _gameRepository.soloMode.endlevel(
          sessionId: _sessionId!,
          playerId: _currentPlayer!.id,
          status: 'win',
          levelPlayed: _currentLevel,
        );
        _currentPlayer = res;

        emit(GameSuccess(finalAttemptsUsed: 999));
        break;
      case GuessOutcome.PLUS:
      case GuessOutcome.MOINS:
        if (result.attemptLeft <= 0) {
          final res = await _gameRepository.soloMode.endlevel(
            sessionId: _sessionId!,
            playerId: _currentPlayer!.id,
            status: 'lose',
            levelPlayed: _currentLevel,
          );
          _currentPlayer = res;
          emit(const GameFailure(reason: "attemps"));
        } else {
          final updatedSession = SoloModeSession(
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
            GameClassicStart(
              session: updatedSession,
              feedbackMessage: feedback,
              lastDistance: result.distance,
            ),
          );
        }
    }
  }

  // DISCOVERY
  Future<void> startDiscoveryGame({required max_range}) async {
    if (_currentPlayer == null) {
      emit(const GameError(errorMessage: "Profil joueur non initialisé."));
      return;
    }
    emit(const GameLoading());

    try {
      final discoverySession = await _gameRepository.discoveryMode.start(
        player_id: _currentPlayer!.id,
        max_range: max_range,
      );
      _sessionId = discoverySession.sessionId;

      emit(GameDiscoveryStart(session: discoverySession));
    } catch (e) {
      emit(GameError(errorMessage: e.toString()));
    }
  }

  void handleGuessDiscovery({
    required GuessResult result,
    required GameDiscoveryStart currentState,
    required int number,
  }) async {
    switch (result.outcome) {
      case GuessOutcome.OK:
        int attemptsUsed;
        final res = await _gameRepository.discoveryMode.endGameSession(
          sessionId: _sessionId!,
          playerId: _currentPlayer!.id,
        );
        attemptsUsed = res;

        emit(GameSuccess(finalAttemptsUsed: attemptsUsed));
        break;
      case GuessOutcome.PLUS:
      case GuessOutcome.MOINS:
        final updatedSession = DiscoveryModeSession(
          sessionId: currentState.session.sessionId,
          maxRange: currentState.session.maxRange,
        );

        final feedback = result.outcome == GuessOutcome.PLUS
            ? "Plus petit que $number ! 📈"
            : "Plus grand que $number ! 📉";

        emit(
          GameDiscoveryStart(
            session: updatedSession,
            feedbackMessage: feedback,
            lastDistance: result.distance,
          ),
        );
    }
  }
}

class DiscoveryWrapper {
  const DiscoveryWrapper();
}
