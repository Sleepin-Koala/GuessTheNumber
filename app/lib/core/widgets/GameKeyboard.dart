import 'package:flutter/material.dart';
import "../theme/app_colors.dart";
import "../theme/app_typography.dart";


class GameKeyboard extends StatelessWidget {
  final Function(String) onKeyTap;
  final VoidCallback onDeleteTap;
  final VoidCallback onSubmitTap;

  const GameKeyboard({
    super.key,
    required this.onKeyTap,
    required this.onDeleteTap,
    required this.onSubmitTap,
  });

  static const List<Color> _rowColors = [
    Color(0xFF4FACFE),
    Color(0xFFA78BFA),
    Color(0xFFFB923C),
  ];
  static const List<Color> _rowShadows = [
    Color(0xFF1565C0),
    Color(0xFF5B21B6),
    Color(0xFF9A3412),
  ];

  @override
  Widget build(BuildContext context) {
    final List<List<String>> keys = [
      ['1', '2', '3'],
      ['4', '5', '6'],
      ['7', '8', '9'],
    ];

    return LayoutBuilder(
      builder: (context, constraints) {
        final screenHeight = MediaQuery.of(context).size.height;

        // Taille de bouton dérivée de la largeur ET bornée par la hauteur d'écran
        double buttonSize = constraints.maxWidth / 3.6;
        if (screenHeight < 700) {
          buttonSize = buttonSize.clamp(48.0, 68.0);
        } else if (screenHeight < 800) {
          buttonSize = buttonSize.clamp(56.0, 78.0);
        } else {
          buttonSize = buttonSize.clamp(64.0, 90.0);
        }

        final rowSpacing = buttonSize * 0.11;
        final fontSize = buttonSize * 0.29;

        return Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ...keys.asMap().entries.map((entry) {
              final rowIndex = entry.key;
              final row = entry.value;
              return Padding(
                padding: EdgeInsets.only(bottom: rowSpacing),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: row
                      .map(
                        (key) => KeyboardButton(
                          size: buttonSize,
                          onPressed: () => onKeyTap(key),
                          color: _rowColors[rowIndex],
                          shadowColor: _rowShadows[rowIndex],
                          child: Text(
                            key,
                            style: AppTypography.display(
                              color: Colors.white,
                              fontSize: fontSize,
                            ),
                          ),
                        ),
                      )
                      .toList(),
                ),
              );
            }),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                KeyboardButton(
                  size: buttonSize,
                  onPressed: onDeleteTap,
                  color: AppColors.danger,
                  shadowColor: const Color(0xFFB71C1C),
                  child: const Center(),
                ),
                KeyboardButton(
                  size: buttonSize,
                  onPressed: () => onKeyTap("0"),
                  color: _rowColors[0],
                  shadowColor: _rowShadows[0],
                  child: Text(
                    '0',
                    style: TextStyle(
                      fontSize: fontSize,
                      fontWeight: FontWeight.w900,
                      color: Colors.white,
                    ),
                  ),
                ),
                KeyboardButton(
                  size: buttonSize,
                  onPressed: onSubmitTap,
                  color: AppColors.success,
                  shadowColor: const Color(0xFF1B5E20),
                  child: const Center(),
                ),
              ],
            ),
          ],
        );
      },
    );
  }
}

class KeyboardButton extends StatefulWidget {
  final Widget child;
  final Color color;
  final Color shadowColor;
  final VoidCallback onPressed;
  final double size;

  const KeyboardButton({
    super.key,
    required this.child,
    required this.onPressed,
    required this.color,
    required this.shadowColor,
    required this.size,
  });

  @override
  State<KeyboardButton> createState() => KeyboardButtonState();
}

class KeyboardButtonState extends State<KeyboardButton> {
  bool _isPressed = false;
  int _bounceKey = 0;

  @override
  Widget build(BuildContext context) {
    final double shadowHeight = widget.size * 0.055;

    return GestureDetector(
      onTapDown: (_) => setState(() => _isPressed = true),
      onTapUp: (_) {
        setState(() {
          _isPressed = false;
          _bounceKey++;
        });
        widget.onPressed();
      },
      onTapCancel: () => setState(() => _isPressed = false),
      child: TweenAnimationBuilder<double>(
        key: ValueKey(_bounceKey),
        tween: Tween<double>(begin: 0.75, end: 1.0),
        duration: const Duration(milliseconds: 320),
        curve: Curves.elasticOut,
        builder: (context, scale, child) {
          return Transform.scale(scale: scale, child: child);
        },
        child: AnimatedContainer(
          height: widget.size,
          width: widget.size,
          duration: const Duration(milliseconds: 50),
          margin: EdgeInsets.only(top: _isPressed ? shadowHeight : 0),
          decoration: BoxDecoration(
            color: widget.color,
            shape: BoxShape.circle,
            border: Border.all(color: Colors.black, width: 3),
            boxShadow: _isPressed
                ? []
                : [
                    BoxShadow(
                      color: widget.shadowColor,
                      offset: Offset(0, shadowHeight),
                      blurRadius: 0,
                    ),
                  ],
          ),
          child: Center(child: widget.child),
        ),
      ),
    );
  }
}