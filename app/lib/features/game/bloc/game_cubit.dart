import 'dart:async';

import 'package:app/data/models/duel_room.dart';
import 'package:app/data/models/discovery_mode_session.dart';
import 'package:app/data/models/endless_mode.dart';
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
  late Timer? _timerPolling;
  late DuelRoom? _currentRoom;
  GameData _gamedata = GameData();

  GameCubit({
    required GameRepository gameRepository,
    required UserRepository userRepository,
  }) : _gameRepository = gameRepository,
       _userRepository = userRepository,
       super(GameInitial(player: null));

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
        _currentPlayer = await _userRepository.getActualPlayer(SettingsService.playerId);
      }

      emit(GameInitial(player: _currentPlayer!));
    } catch (e) {
      _currentPlayer = await _userRepository.getNewPlayer();
      SettingsService.setData(_currentPlayer!.id);
      emit(GameInitial(player: _currentPlayer!));
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

  void onDuelMode() {
    emit(GameDuelSelectVariant());
  }

  void resetToHome() {
    emit(GameInitial(player: _currentPlayer));
  }

  // ENDLESS

  Future<void> startEndlessGame(int bet) async {
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
        stage: 1,
      );
      _sessionId = endlessSession.sessionId;
      _currentPlayer = _currentPlayer!.copyWith(
        coins: endlessSession.playerCoins,
      );
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
          emit(
            GameEndlessLose(
              currentStage: currentState.session.stage,
              bet: currentState.session.bet,
            ),
          );
        } else {
          _gamedata = _gamedata.copyWith(
            numberDiscoverAttempt: _gamedata.numberDiscoverAttempt + 1,
          );

          print(_gamedata.currentBet);

          final updatedSession = EndlessModeSession(
            sessionId: currentState.session.sessionId,
            maxAttempt: currentState.session.maxAttempt,
            attemptLeft: result.attemptLeft,
            maxRange: currentState.session.maxRange,
            bet: _gamedata.currentBet!,
            stage: currentState.session.stage,
            playerCoins: currentState.session.playerCoins,
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
        final int amountWinned = await _gameRepository.endlessMode
            .endGameSession(
              sessionId: _sessionId!,
              playerId: _currentPlayer!.id,
              status: 'win',
            );
        _currentPlayer = _currentPlayer!.copyWith(
          coins: _currentPlayer!.coins + amountWinned,
        );

        emit(
          GameEndlessWin(
            currentStage: currentState.session.stage,
            reward: amountWinned,
          ),
        );
    }
  }

  Future<void> continueEndlessGame(int bet, int stage) async {
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
        stage: stage,
      );
      _sessionId = endlessSession.sessionId;
      _currentPlayer = _currentPlayer!.copyWith(
        coins: endlessSession.playerCoins,
      );
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

  // CLASSIC
  Future<void> startClassicSession({required int level}) async {
    if (_currentPlayer == null) {
      emit(const GameError(errorMessage: "Profil joueur non initialisé."));
      return;
    }
    emit(const GameLoading());
    try {
      final newSession = await _gameRepository.soloMode.start(
        playerId: _currentPlayer!.id,
        level: level,
      );
      _sessionId = newSession.sessionId;
      _currentLevel = level;

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
        _currentPlayer = await _userRepository.getActualPlayer(SettingsService.playerId);
        emit(
          GameClassicWin(
            finalAttemptsUsed: result.maxAttempt - result.attemptLeft,
            currentLevel: _currentLevel,
            coinsEarned: res.coins,
            xpWinned: res.xp,
            starsWinned: res.stars
          ),
        );
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
          _currentPlayer = await _userRepository.getActualPlayer(SettingsService.playerId);
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

        emit(GameDiscoveryWin(attempts: attemptsUsed));
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

  // DUEL

  Future<void> startDuelMode() async {
    try {
      final allRooms = await _gameRepository.duelMode.fetchDuelRooms();
      emit(GameDuelLobby(player: _currentPlayer!, rooms: allRooms));
    } catch (e) {
      emit(GameError(errorMessage: e.toString()));
    }
  }

  Future<void> createDuelRoom(String name, int amount, int maxRange) async {
    try {
      final room = await _gameRepository.duelMode.createDuelRoom(
        _currentPlayer!.id,
        name,
        amount,
        maxRange,
      );
      _currentRoom = room;
      emit(GameDuelRoom(room: room, player: _currentPlayer!));
      startDuelRoomPolling();
    } catch (e) {
      emit(GameError(errorMessage: e.toString()));
    }
  }

  void startDuelRoomPolling() {
    _timerPolling = Timer.periodic(Duration(milliseconds: 1500), (_) async {
      try {
        final room = await _gameRepository.duelMode.checkRoomStatus(
          _currentRoom!.room_id,
        );
        emit(GameDuelRoom(room: room, player: _currentPlayer!));
        if (room.status == DuelStatus.finished) {
          _timerPolling!.cancel();
        }
      } catch (e) {
        emit(GameError(errorMessage: e.toString()));
      }
    });
  }

  void joinDuelRoom(roomId) async {
    try {
      final room = await _gameRepository.duelMode.joinDuelRoom(
        roomId,
        _currentPlayer!.id,
      );
      _currentRoom = room;
      emit(GameDuelRoom(room: room, player: _currentPlayer!));
      startDuelRoomPolling();
    } catch (e) {
      emit(GameError(errorMessage: e.toString()));
    }
  }

  void submitHiddenNumber(int nb) async {
    try {
      final room = await _gameRepository.duelMode.submitHiddenNumber(
        roomId: _currentRoom!.room_id,
        playerId: _currentPlayer!.id,
        secretNumber: nb,
      );
      emit(GameDuelRoom(player: _currentPlayer!, room: room));
    } catch (e) {
      emit(GameError(errorMessage: e.toString()));
    }
  }

  Future<void> submitDuelGuess(int number) async {
    try {
      final room = await _gameRepository.duelMode.submitDuelGuess(
        roomId: _currentRoom!.room_id,
        playerId: _currentPlayer!.id,
        number: number,
      );
      emit(GameDuelRoom(player: _currentPlayer!, room: room));
      if (room.status == DuelStatus.finished) {
        _timerPolling?.cancel();
      }
    } catch (e) {
      emit(GameError(errorMessage: e.toString()));
    }
  }

  Future<void> leaveDuelRoom() async {
    _timerPolling?.cancel();
    _currentRoom = null;
  
    onDuelMode();
  }
}
