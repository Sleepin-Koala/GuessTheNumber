import "../theme/app_colors.dart";
import 'package:flutter/material.dart';
import '../theme/app_typography.dart';

class CartoonCard extends StatefulWidget {
  final VoidCallback onPressed;
  final Color color;
  final Color shadowColor;
  final String title;
  final String description;
  final IconData icon;

  const CartoonCard({
    super.key,
    this.color = AppColors.primary,
    this.shadowColor = AppColors.secondary,
    required this.onPressed,
    required this.title,
    this.description = "",
    required this.icon,
  });

  @override
  State<CartoonCard> createState() => _CartoonCardState();
}

class _CartoonCardState extends State<CartoonCard> {
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
          decoration: BoxDecoration(
            color: widget.color,
            borderRadius: BorderRadius.circular(20),
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
            style: AppTypography.body(fontSize: 18, fontWeight: FontWeight.w700),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  widget.icon,
                  size: 44,
                  color: Colors.white.withOpacity(0.95),
                ),
                Text(
                  widget.title,
                  style: AppTypography.body(
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.5,
                  ),
                  textAlign: TextAlign.center,
                ),
                Text(
                  widget.description,
                  style: AppTypography.body(
                    fontSize: 15,
                    fontWeight: FontWeight.w500,
                    color: Colors.white.withOpacity(0.85),
                  ),
                  textAlign: TextAlign.center,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
