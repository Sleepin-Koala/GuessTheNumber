import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

class CartoonIconButton extends StatefulWidget {
  final IconData? icon;
  final Widget? child; 
  final Color color;
  final Color shadowColor;
  final VoidCallback onPressed;
  final double size;

  const CartoonIconButton({
    super.key,
    this.icon,
    this.child,
    this.color = AppColors.cardBg,
    this.shadowColor = Colors.black,
    required this.onPressed,
    this.size = 56,
  });

  @override
  State<CartoonIconButton> createState() => _CartoonIconButtonState();
}

class _CartoonIconButtonState extends State<CartoonIconButton> {
  bool _isPressed = false;

  @override
  Widget build(BuildContext context) {
    const double shadowHeight = 5;

    return GestureDetector(
      onTapDown: (_) => setState(() => _isPressed = true),
      onTapUp: (_) {
        setState(() => _isPressed = false);
        widget.onPressed();
      },
      onTapCancel: () => setState(() => _isPressed = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 50),
        margin: EdgeInsets.only(top: _isPressed ? shadowHeight : 0),
        width: widget.size,
        height: widget.size,
        decoration: BoxDecoration(
          color: widget.color,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.black, width: 3),
          boxShadow: _isPressed
              ? []
              : [
                  BoxShadow(
                    color: widget.shadowColor,
                    offset: const Offset(0, shadowHeight),
                    blurRadius: 0,
                  ),
                ],
        ),
        child: Center(
          child: widget.child ??
              Icon(widget.icon, color: Colors.white, size: widget.size * 0.42),
        ),
      ),
    );
  }
}
