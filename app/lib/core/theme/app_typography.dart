import 'package:google_fonts/google_fonts.dart';
import 'package:flutter/material.dart';

class AppTypography {
  AppTypography._();

  static TextStyle display({double fontSize = 48, Color color = Colors.white}) {
    return GoogleFonts.luckiestGuy(
      textStyle: TextStyle(fontSize: fontSize, color: color, height: 1.0),
    );
  }

  static TextStyle body({
    double fontSize = 16,
    FontWeight fontWeight = FontWeight.w600,
    Color color = Colors.white,
    double? letterSpacing,
  }) {
    return GoogleFonts.baloo2(
      textStyle: TextStyle(
        fontSize: fontSize,
        fontWeight: fontWeight,
        color: color,
        letterSpacing: letterSpacing,
      ),
    );
  }
}
