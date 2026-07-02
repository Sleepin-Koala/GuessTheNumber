import "package:app/core/theme/app_colors.dart";
import "package:app/features/game/bloc/game_cubit.dart";
import "package:app/features/game/views/game_screen.dart";
import 'package:flutter/material.dart';
import "package:flutter_bloc/flutter_bloc.dart";
import "data/repositories/game_repository.dart";
import "data/repositories/user_repository.dart";
import 'package:google_fonts/google_fonts.dart';

void main() {
  final gameRepository = GameRepository();
  final userRepository = UserRepository();

  runApp(
    MultiRepositoryProvider(
      providers: [
        RepositoryProvider<GameRepository>.value(value: gameRepository),
        RepositoryProvider<UserRepository>.value(value: userRepository),
      ],
      child: MultiBlocProvider(
        providers: [
          BlocProvider<GameCubit>(
            create: (context) => GameCubit(
              gameRepository: gameRepository,
              userRepository: userRepository,
            )..initializeApp(),
          ),
        ],
        child: const GuessTheNumberApp(),
      ),
    ),
  );
}

class GuessTheNumberApp extends StatelessWidget {
  const GuessTheNumberApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "Guess The Number",
      theme: ThemeData(
        scaffoldBackgroundColor: AppColors.background,
        useMaterial3: true,

        textTheme: GoogleFonts.baloo2TextTheme(
          const TextTheme(
            labelLarge: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),

            bodyLarge: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
            bodyMedium: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),

      home: const GameScreen(),
    );
  }
}
