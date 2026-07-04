import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

class CartoonIcon extends StatelessWidget {
  final String assetPath;
  final double size;

  const CartoonIcon({super.key, this.size = 28 , required this.assetPath,});

  @override
  Widget build(BuildContext context) {
    return SvgPicture.asset(
      assetPath,
      width: size,
      height: size,
      fit: BoxFit.contain,
    );
  }
}