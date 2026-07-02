import 'package:flutter/material.dart';
import "../theme/app_colors.dart";

class CartoonButton extends StatefulWidget {
  final Color color;
  final Color shadowColor;
  final Widget child;
  final VoidCallback onPressed;
  final double? height;

  const CartoonButton({
    super.key,
    this.color = AppColors.primary,
    this.height,
    this.shadowColor = AppColors.secondary,
    required this.child,
    required this.onPressed,
  });

  @override
  State<CartoonButton> createState() => _CartoonButtonState();
}

class _CartoonButtonState extends State<CartoonButton> {
  bool _isPressed = false;

  @override
  Widget build(BuildContext context) {
    final double shadowHeight = 6;

    return GestureDetector(
      onTapDown: (_) => setState(() {
        _isPressed = true;
      }),
      onTapUp: (_) {
        setState(() => _isPressed = false);
        widget.onPressed();
      },
      onTapCancel: () => setState(() => _isPressed = false),

      child: AnimatedContainer(
        duration: const Duration(milliseconds: 50),
        padding: EdgeInsets.only(
          top: _isPressed ? shadowHeight : 0,
          bottom: _isPressed ? 0 : shadowHeight,
        ),

        child: Container(
          height: widget.height,
          decoration: BoxDecoration(
            color: widget.color,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.black, width: 3),
            boxShadow: _isPressed
                ? [] // Pas d'ombre quand enfoncé
                : [
                    BoxShadow(
                      color: widget.shadowColor,
                      offset: Offset(0, shadowHeight),
                      blurRadius: 0,
                    ),
                  ],
          ),
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 24),
          child: DefaultTextStyle(
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
              shadows: [
                Shadow(
                  color: Colors.black,
                  offset: Offset(1.5, 1.5),
                  blurRadius: 0,
                ),
              ],
            ),
            child: widget.child,
          ),
        ),
      ),
    );
  }
}
