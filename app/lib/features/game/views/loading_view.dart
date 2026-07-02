import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';



class LoadingView extends StatelessWidget {
  const LoadingView({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
            strokeWidth: 6,
          ),
          SizedBox(height: 24),
          Text(
            'CONNEXION AU SERVEUR...',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w900,
              letterSpacing: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}