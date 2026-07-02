

import 'package:flutter/material.dart';
import '../../../../core/theme/app_typography.dart';

class ShakingText extends StatefulWidget {
  final String text;

  ShakingText({required this.text}) : super(key: ValueKey(text));

  @override
  State<ShakingText> createState() => _ShakingTextState();
}

class _ShakingTextState extends State<ShakingText> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );



  _scaleAnimation = CurvedAnimation(
      parent: _controller,
      curve: Curves.elasticOut,
    );

  _controller.forward();
}


  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ScaleTransition(
      scale: _scaleAnimation,
      child: Text(
        widget.text,
        textAlign: TextAlign.center,
        style: AppTypography.body(color: Colors.white, fontSize: 22, fontWeight: FontWeight.w900)
        ),
      );
  }
}