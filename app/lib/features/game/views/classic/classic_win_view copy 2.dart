import 'package:flutter/material.dart';
import 'dart:math' as math;



/// Écran de victoire avec animation des étoiles (1 à 3).
class LevelWinScreen extends StatefulWidget {
  const LevelWinScreen({super.key});

  @override
  State<LevelWinScreen> createState() => _LevelWinScreenState();
}

class _LevelWinScreenState extends State<LevelWinScreen>
    with TickerProviderStateMixin {
  // Nombre d’étoiles obtenues (1, 2 ou 3). À calculer selon la performance.
  int starsEarned = 3;

  // État d’animation pour chaque étoile : 0 = pas encore arrivée, 1 = arrivée.
  final List<int> _starState = [0, 0, 0];

  // Contrôleurs d’animation pour chaque étoile (position + scale).
  final List<AnimationController> _controllers = [];
  final List<Animation<Offset>> _slideAnimations = [];
  final List<Animation<double>> _scaleAnimations = [];

  @override
  void initState() {
    super.initState();
    _initStarAnimations();
  }

  void _initStarAnimations() {
    // On crée un contrôleur par étoile possible (3 max).
    for (int i = 0; i < 3; i++) {
      final controller = AnimationController(
        duration: const Duration(milliseconds: 600),
        vsync: this,
      );

      // Animation de glissement : du bas vers le centre de l’emplacement.
      final slideAnim = Tween<Offset>(
        begin: const Offset(0, 1.2), // part d’en bas de l’écran
        end: Offset.zero,
      ).animate(CurvedAnimation(
        parent: controller,
        curve: Curves.elasticOut,
      ));

      // Animation d’échelle : effet de “pop” quand l’étoile arrive.
      final scaleAnim = Tween<double>(
        begin: 0.0,
        end: 1.0,
      ).animate(CurvedAnimation(
        parent: controller,
        curve: Curves.bounceIn,
      ));

      _controllers.add(controller);
      _slideAnimations.add(slideAnim);
      _scaleAnimations.add(scaleAnim);
    }

    // Lancer les animations avec un délai entre chaque étoile.
    _startStarAnimations();
  }

  void _startStarAnimations() {
    for (int i = 0; i < 3; i++) {
      if (i < starsEarned) {
        // Délai progressif : 0ms, 400ms, 800ms par exemple.
        Future.delayed(Duration(milliseconds: i * 400), () {
          if (!mounted) return;
          _controllers[i].forward();
          _starState[i] = 1;
        });
      } else {
        // Pas d’étoile pour cet emplacement : on garde l’état 0.
        _starState[i] = 0;
      }
    }
  }

  @override
  void dispose() {
    for (final c in _controllers) {
      c.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D1117), // fond sombre style arcade
      body: SafeArea(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              'VICTOIRE !',
              style: TextStyle(
                fontSize: 36,
                fontWeight: FontWeight.bold,
                color: Colors.white,
                letterSpacing: 2,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Niveau terminé',
              style: TextStyle(
                fontSize: 18,
                color: Colors.white.withOpacity(0.8),
              ),
            ),
            const SizedBox(height: 48),

            // Zone des étoiles avec leurs placeholders
            SizedBox(
              height: 120,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(3, (index) => _buildStarSlot(index)),
              ),
            ),

            const SizedBox(height: 48),

            // Bouton pour rejouer / niveau suivant
            ElevatedButton(
              onPressed: () {
                // Navigator, reload, etc.
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.amber,
                foregroundColor: Colors.black,
                padding: const EdgeInsets.symmetric(
                  horizontal: 32,
                  vertical: 16,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Text(
                'Continuer',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStarSlot(int index) {
    final hasStar = index < starsEarned;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      child: SizedBox(
        width: 80,
        height: 80,
        child: Stack(
          alignment: Alignment.center,
          children: [
            // Placeholder (socle / encoche)
            _buildStarPlaceholder(),

            // Étoile animée (si obtenue)
            if (hasStar)
              SlideTransition(
                position: _slideAnimations[index],
                child: ScaleTransition(
                  scale: _scaleAnimations[index], 
                  child: const _StarWidget(),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildStarPlaceholder() {
    return Container(
      width: 70,
      height: 70,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(
          color: Colors.white.withOpacity(0.25),
          width: 2,
        ),
        color: Colors.white.withOpacity(0.05),
      ),
      child: const Icon(
        Icons.star_border,
        size: 40,
        color: Colors.white38,
      ),
    );
  }
}

/// Widget d’une étoile pleine (style arcade).
class _StarWidget extends StatelessWidget {
  const _StarWidget();

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      size: const Size(70, 70),
      painter: _StarPainter(),
    );
  }
}

class _StarPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFFFFD54A) // jaune/or
      ..style = PaintingStyle.fill
      ..strokeJoin = StrokeJoin.round
      ..strokeCap = StrokeCap.round;

    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width * 0.45;

    final path = _createStarPath(center, radius, 5);
    canvas.drawPath(path, paint);
  }

  Path _createStarPath(Offset center, double radius, int points) {
    final path = Path();
    final angleStep = math.pi / points;

    // On commence en haut
    double angle = -math.pi / 2;

    path.moveTo(
      center.dx + radius * math.cos(angle),
      center.dy + radius * math.sin(angle),
    );

    for (int i = 0; i < points; i++) {
      // Point extérieur
      angle += angleStep;
      path.lineTo(
        center.dx + radius * math.cos(angle),
        center.dy + radius * math.sin(angle),
      );

      // Point intérieur (creux de l’étoile)
      angle += angleStep;
      final innerRadius = radius * 0.45;
      path.lineTo(
        center.dx + innerRadius * math.cos(angle),
        center.dy + innerRadius * math.sin(angle),
      );
    }

    path.close();
    return path;
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}