import 'package:app/data/models/GameMode.dart';
import 'package:flutter/material.dart';
import '../widgets/CartoonCard.dart';

class ModeCarousel extends StatefulWidget {
  final List<GameMode> modes;
  final void Function(GameMode modes) onModeSelected;

  const ModeCarousel({super.key, required this.modes , required this.onModeSelected});

  @override
  State<ModeCarousel> createState() => _ModeCarouselState();
}

class _ModeCarouselState extends State<ModeCarousel> {
  int _currentPage = 0;
  late final PageController _pageController;

  @override
  void initState() {
    super.initState();
    _pageController = PageController(viewportFraction: 0.82);
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(
          child: PageView.builder(
            controller: _pageController,
            itemCount: widget.modes.length,
            onPageChanged: (index) => setState(() => _currentPage = index),
            itemBuilder: (context, index) {
              final mode = widget.modes[index];

              return AnimatedBuilder(
                animation: _pageController,
                builder: (context, child) {
                  double scale = 1.0;
                  double opacity = 1.0;
                  if (_pageController.position.haveDimensions) {
                    final page = _pageController.page ?? _currentPage.toDouble();
                    final distance = (page - index).abs();
                    scale = (1 - (distance * 0.15)).clamp(0.85, 1.0);
                    opacity = (1 - (distance * 0.5)).clamp(0.4, 1.0);
                  }
                  return Center(
                    child: Opacity(
                      opacity: opacity,
                      child: Transform.scale(scale: scale, child: child),
                    ),
                  );
                },

                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                  child: CartoonCard(
                    onPressed: ()=>widget.onModeSelected(mode),
                    title: mode.title,
                    color: mode.color,
                    shadowColor: mode.shadowColor,
                    icon: mode.icon,
                    description: mode.description,
                  ),
                ),
              );
            },
          ),
        ),

        const SizedBox(height: 16),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(widget.modes.length, (index) {
            final isActive = index == _currentPage;
            return AnimatedContainer(
              duration: const Duration(milliseconds: 250),
              margin: const EdgeInsets.symmetric(horizontal: 4),
              width: isActive ? 22 : 8,
              height: 8,
              decoration: BoxDecoration(
                color: isActive
                    ? widget.modes[_currentPage].color
                    : Colors.white24,
                borderRadius: BorderRadius.circular(4),
              ),
            );
          }),
        ),
      ],
    );
  }
}
