import 'dart:math';
import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

/// Fond animé : quelques "orbes" lumineuses floues qui dérivent lentement
/// en arrière-plan, façon nébuleuse douce. Donne de la profondeur à un
/// fond qui était avant une couleur plate uniforme.
///
/// Pourquoi CustomPainter plutôt que des Container empilés dans un Stack ?
/// Parce qu'on anime en continu (boucle infinie) — avec CustomPainter,
/// TOUT se dessine sur une seule "toile" (Canvas) en un seul repaint par
/// frame, au lieu de faire recalculer le layout de 4 widgets séparés à
/// chaque frame. Plus léger, et c'est l'outil qu'on réutilisera pour la
/// mascotte plus tard.
class AnimatedGameBackground extends StatefulWidget {
  const AnimatedGameBackground({super.key});

  @override
  State<AnimatedGameBackground> createState() => _AnimatedGameBackgroundState();
}

class _AnimatedGameBackgroundState extends State<AnimatedGameBackground>
    with SingleTickerProviderStateMixin {
  // Un AnimationController ne représente qu'UNE chose : une valeur qui
  // évolue dans le temps (ici de 0.0 à 1.0). Il ne sait pas dessiner quoi
  // que ce soit tout seul — c'est le CustomPainter, juste après, qui lit
  // cette valeur pour savoir où placer les orbes à chaque instant.
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this, // "vsync" synchronise l'animation sur le rafraîchissement
      // de l'écran (évite de dessiner des frames que l'utilisateur ne
      // verra jamais). SingleTickerProviderStateMixin fournit ce vsync.
      duration: const Duration(seconds: 26),
    )..repeat(); // boucle à l'infini, de 0.0 à 1.0 puis retour à 0.0

  }

  @override
  void dispose() {
    // Toujours libérer un AnimationController : sinon il continue de
    // tourner en arrière-plan même après que le widget a disparu de
    // l'écran — fuite mémoire classique en Flutter.
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // AnimatedBuilder reconstruit SEULEMENT le CustomPaint à chaque tick
    // de l'animation, pas tout l'écran parent — c'est ce qui rend
    // l'animation peu coûteuse même si HomeView/PlayingView ont beaucoup
    // d'autres widgets autour.
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return CustomPaint(
          painter: _BackgroundPainter(_controller.value),
          size: Size.infinite, // occupe tout l'espace disponible
        );
      },
    );
  }
}

/// Description d'une orbe : sa couleur, sa position de base (en fraction
/// 0.0->1.0 de l'écran, pas en pixels — ça la rend responsive à n'importe
/// quelle taille d'écran), l'amplitude de son déplacement, sa vitesse et
/// son déphasage (pour que les orbes ne bougent pas toutes en même temps).
class _Orb {
  final Color color;
  final double baseX, baseY;
  final double driftX, driftY;
  final double speed;
  final double phase;
  final double radiusFraction;

  const _Orb({
    required this.color,
    required this.baseX,
    required this.baseY,
    required this.driftX,
    required this.driftY,
    required this.speed,
    required this.phase,
    required this.radiusFraction,
  });
}

class _BackgroundPainter extends CustomPainter {
  final double t; // valeur 0.0 -> 1.0 fournie par l'AnimationController

  _BackgroundPainter(this.t);

  static final List<_Orb> _orbs = [
    _Orb(
      color: AppColors.primary,
      baseX: 0.2, baseY: 0.25,
      driftX: 0.10, driftY: 0.08,
      speed: 1.0, phase: 0,
      radiusFraction: 0.35,
    ),
    _Orb(
      color: AppColors.secondary,
      baseX: 0.85, baseY: 0.15,
      driftX: 0.08, driftY: 0.10,
      speed: 0.7, phase: pi / 2,
      radiusFraction: 0.30,
    ),
    _Orb(
      color: const Color(0xFF7B5FFF), // violet accent, proche de cardBg
      baseX: 0.75, baseY: 0.8,
      driftX: 0.09, driftY: 0.07,
      speed: 0.85, phase: pi,
      radiusFraction: 0.38,
    ),
    _Orb(
      color: AppColors.success,
      baseX: 0.15, baseY: 0.85,
      driftX: 0.07, driftY: 0.09,
      speed: 1.2, phase: pi * 1.4,
      radiusFraction: 0.25,
    ),
  ];

  @override
  void paint(Canvas canvas, Size size) {
    for (final orb in _orbs) {
      // sin/cos de (t * 2π * vitesse + déphasage) : ça produit un
      // mouvement cyclique fluide qui revient exactement à son point de
      // départ quand t reboucle de 1.0 à 0.0 — pas de "saut" visible.
      final angle = t * 2 * pi * orb.speed + orb.phase;
      final dx = (orb.baseX + sin(angle) * orb.driftX) * size.width;
      final dy = (orb.baseY + cos(angle * 0.8) * orb.driftY) * size.height;
      final center = Offset(dx, dy);
      final radius = orb.radiusFraction * size.shortestSide;

      // RadialGradient en tant que "shader" : au lieu d'une couleur unie,
      // le Paint applique un dégradé qui part d'une couleur semi-opaque
      // au centre et se fond en totale transparence sur les bords. C'est
      // ce qui donne l'effet "lueur floue" sans utiliser de vrai flou
      // gaussien (beaucoup plus coûteux en performance à chaque frame).
      final paint = Paint()
        ..shader = RadialGradient(
          colors: [
            orb.color.withOpacity(0.32),
            orb.color.withOpacity(0.0),
          ],
        ).createShader(Rect.fromCircle(center: center, radius: radius));

      canvas.drawCircle(center, radius, paint);
    }
  }

  @override
  bool shouldRepaint(covariant _BackgroundPainter oldDelegate) {
    // On ne redessine que si la valeur d'animation a changé — évite un
    // repaint inutile si jamais ce painter était reconstruit sans que le
    // temps ait avancé.
    return oldDelegate.t != t;
  }
}
