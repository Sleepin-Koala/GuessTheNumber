import 'package:flutter/material.dart';
import "../theme/app_colors.dart";
import "package:lucide_icons/lucide_icons.dart";
import "./CartoonButton.dart";

class GameKeyboard extends StatelessWidget {

  final Function(String) onKeyTap;
  final VoidCallback onDeleteTap;
  final VoidCallback onSubmitTap;

  const GameKeyboard({super.key, required this.onKeyTap , required this.onDeleteTap , required this.onSubmitTap});

  @override
  Widget build(BuildContext context) {
    final List<List<String>> keys = [
      ['1', '2', '3'],
      ['4', '5', '6'],
      ['7', '8', '9'],
    ];

    return Column(
      children: [
        ...keys.map(
          (row) => Padding(
            padding: const EdgeInsets.only(bottom: 12.0),
            child: Row(
              children: row
                  .map(
                    (key) => Expanded(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 6.0),
                        child: CartoonButton(
                          onPressed: () => onKeyTap(key),
                          color: AppColors.cardBg,
                          shadowColor: Colors.black,
                          child: Text(
                            key,
                            style: const TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.w900,
                            ),
                          ),
                        ),
                      ),
                    ),
                  )
                  .toList(),
            ),
          ),
        ),

        Row(
          children: [
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 6.0),
                child: CartoonButton(
                  onPressed: onDeleteTap,
                  color: AppColors.danger,
                  shadowColor: const Color(0xFFB71C1C),
                  child: const Icon(LucideIcons.space, color: Colors.white),
                ),
              ),
            ),

            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 6.0),
                child: CartoonButton(
                  onPressed: () => onKeyTap("0"),
                  color: AppColors.cardBg,
                  shadowColor: Colors.black,
                  child: const Text(
                    '0',
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900),
                  ),
                ),
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 6.0),
                child: CartoonButton(
                  onPressed: onSubmitTap,
                  color: AppColors.success,
                  shadowColor: const Color(0xFF1B5E20),
                  child: const Icon(LucideIcons.check, color: Colors.white),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

