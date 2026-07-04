import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../bloc/game_cubit.dart';
import '../bloc/game_state.dart';
import '../../../data/models/GameMode.dart';
import '../../../core/widgets/progress_banner.dart';
import '../../../core/widgets/mode_carousel.dart';

class MenuView extends StatelessWidget {
  const MenuView({super.key});

  static const List<GameMode> modes = [
    GameMode(
      id: 'classic',
      title: 'CLASSIQUE',
      description:
          'Trouve le nombre mystère en un minimum d\'essais. Chronométré !',
      icon: LucideIcons.shieldAlert,
      color: Color(0xFF4FACFE),
      gradientEnd: Color(0xFF1D4ED8),
      shadowColor: Color(0xFF1E3A8A),
    ),
    GameMode(
      id: 'discovery',
      title: 'DÉCOUVERTE',
      description: 'Apprends les règles pas à pas. Des indices t\'aideront.',
      icon: LucideIcons.compass,
      color: Color(0xFF34D399),
      gradientEnd: Color(0xFF059669),
      shadowColor: Color(0xFF065F46),
    ),
    GameMode(
      id: 'duel',
      title: 'DUEL',
      description: 'Affronte un autre joueur au tour par tour.',
      icon: LucideIcons.swords,
      color: Color(0xFFFB923C),
      gradientEnd: Color(0xFFEA580C),
      shadowColor: Color(0xFF9A3412),
    )
  ];

  @override
  Widget build(BuildContext context) {
    final cubitState = context.read<GameCubit>().state;
    if (cubitState is! GameMenu) return const SizedBox.shrink();
    final player = cubitState.player;

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,

        children: [
          PlayerProgressBanner(player: player),
          const SizedBox(height : 32),
          Expanded(child: 
          ModeCarousel(
            modes: modes,
            onModeSelected: (mode)=> {
              switch (mode.id) {
                "classic" => context.read<GameCubit>().onLevelSelection(),
                "discovery" => context.read<GameCubit>().onDiscoveryPage(),
                "duel" => (){},
                String() => throw UnimplementedError(),
              }
            },
            
            ))    
        ],
      ),
    );
  }
}
