import 'package:app/features/game/bloc/game_cubit.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../core/theme/app_typography.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_icon.dart';
import '../../core/widgets/CartoonIcon.dart';
import '../../core/widgets/CartoonButton.dart';
import '../../core/widgets/cartoon_icon_button.dart';

class _TutorialSlide {
  final String emoji;
  final String title;
  final String body;
  const _TutorialSlide({
    required this.emoji,
    required this.title,
    required this.body,
  });
}

const List<_TutorialSlide> _slides = [
  _TutorialSlide(
    emoji: "🎯",
    title: "Bienvenue en Découverte",
    body:
        "Pas de chrono, pas de limite d'essais. L'endroit parfait pour "
        "t'entraîner et comprendre le jeu à ton rythme.",
  ),
  _TutorialSlide(
    emoji: "🌡️",
    title: "La jauge de température",
    body:
        "Après chaque essai, une jauge te montre à quel point tu es "
        "proche du nombre secret : bleu = froid, rouge = brûlant.",
  ),
  _TutorialSlide(
    emoji: "🔼",
    title: "Plus grand, plus petit",
    body:
        "En plus de la jauge, un message te dit si le nombre secret est "
        "plus grand ou plus petit que ta proposition.",
  ),
  _TutorialSlide(
    emoji: "🎚️",
    title: "À toi de choisir",
    body:
        "Sur l'écran suivant, choisis la plage dans laquelle chercher : "
        "de 1 à 10 pour t'échauffer, jusqu'à 1 à 1000 pour un vrai défi.",
  ),
];

class TutorialCarousel extends StatefulWidget {
  final VoidCallback onDone;
  const TutorialCarousel({required this.onDone, super.key});

  @override
  State<TutorialCarousel> createState() => TutorialCarouselState();
}

class TutorialCarouselState extends State<TutorialCarousel> {
  final PageController _controller = PageController();
  int _page = 0;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _goNext() {
    if (_page == _slides.length - 1) {
      widget.onDone();
    } else {
      _controller.nextPage(
        duration: const Duration(milliseconds: 350),
        curve: Curves.easeOutCubic,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isLast = _page == _slides.length - 1;

    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            CartoonIconButton(
              child: CartoonIcon(assetPath: AppIcons.close),
              onPressed: () => context.read<GameCubit>().onMenu(),
            ),
            TextButton(
              onPressed: widget.onDone,
              child: Text(
                "Passer",
                style: AppTypography.body(
                  color: Colors.white54,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ],
        ),

        Expanded(
          child: PageView.builder(
            controller: _controller,
            itemCount: _slides.length,
            onPageChanged: (i) => setState(() => _page = i),
            itemBuilder: (context, index) {
              final slide = _slides[index];
              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8),
                child: Container(
                  padding: const EdgeInsets.all(28),
                  decoration: BoxDecoration(
                    color: AppColors.cardBg,
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: Colors.black, width: 3),
                  ),

                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(slide.emoji, style: const TextStyle(fontSize: 64)),
                      const SizedBox(height: 20),
                      Text(
                        slide.title,
                        textAlign: TextAlign.center,
                        style: AppTypography.display(fontSize: 26),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        slide.body,
                        textAlign: TextAlign.center,
                        style: AppTypography.body(
                          fontSize: 16,
                          fontWeight: FontWeight.w500,
                          color: Colors.white70,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 16),

        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(_slides.length, (index) {
            final isActive = index == _page;
            return AnimatedContainer(
              duration: const Duration(milliseconds: 250),
              margin: const EdgeInsets.symmetric(horizontal: 4),
              width: isActive ? 22 : 8,
              height: 8,
              decoration: BoxDecoration(
                color: isActive ? AppColors.primary : Colors.white24,
                borderRadius: BorderRadius.circular(4),
              ),
            );
          }),
        ),
        const SizedBox(height: 20),

        CartoonButton(
          onPressed: _goNext,
          color: AppColors.primary,
          shadowColor: AppColors.secondary,
          child: Text(
            isLast ? "COMMENCER" : "SUIVANT",
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
        ),
      ],
    );
  }
}
