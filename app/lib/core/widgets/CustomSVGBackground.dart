import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

class CustomSVGBackground extends StatelessWidget {
  final String assetPath;

  const CustomSVGBackground(this.assetPath, {super.key} );

  @override
  Widget build(BuildContext context) {
    return SvgPicture.asset(
      assetPath,
      width: MediaQuery.sizeOf(context).width,
      height: MediaQuery.sizeOf(context).height,
      fit: BoxFit.contain,
    );
  }
}