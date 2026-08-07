import 'package:flutter/material.dart';
import 'package:app/features/game/bloc/game_state.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../bloc/game_cubit.dart';
import '../../../../data/models/player.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_typography.dart';
import '../../../../core/theme/app_icon.dart';
import '../../../../core/widgets/cartoonIcon.dart';
import '../../../../core/widgets/cartoonButton.dart';

import '../../../../core/widgets/progress_banner.dart';

class EndlessStartView extends StatefulWidget {
  const EndlessStartView({super.key});

  @override
  State<EndlessStartView> createState() => _EndlessStartViewState();
}

class _EndlessStartViewState extends State<EndlessStartView> {
  int? _selectedInput;
  String? _errorText;
  late int bet;
  final List<int> inputs = [100, 300, 500, 800, 1000, 2000, 3000, 5000];
  final TextEditingController _controller = TextEditingController();
  bool _isCustom = false;

  void _handlePlay(coins) {

    if (_selectedInput == 0) bet = int.parse(_controller.text);



    if (coins >= bet) {
      context.read<GameCubit>().startEndlessGame(bet);
    } else {
      setState(() {
        _errorText = "tu n'as pas assez d'argent";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    GameState state = context.read<GameCubit>().state;
    if (state is! GameEndlessStart) return const SizedBox.shrink();

    Player player = state.player;

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            PlayerProgressBanner(player: player),
            const SizedBox(height: 32),
            Text("FAIT TA MISE", style: AppTypography.display(fontSize: 28)),
            const SizedBox(height: 16),
            Text(
              "apres la mise aucune possibilité d'avoir de la reprendre exepté la victoire.",
              textAlign: TextAlign.center,
              style: AppTypography.body(fontSize: 14, color: Colors.white70),
            ),

            const SizedBox(height: 16),

            Wrap(
              children: inputs.map((item) {
                return _buildChip(
                  label: item.toString(),
                  isSelected: _selectedInput == item,
                  onTap: () {
                    setState(() {
                      _selectedInput = item;
                      bet = item;
                      _isCustom = false;
                      
                    });
                  },
                );
              }).toList(),
            ),
            _buildChip(
                  label: "personnalisé",
                  isSelected: _selectedInput == 0,
                  onTap: () {
                    setState(() {
                      _selectedInput = 0;
                      _isCustom = true;
                    });
                  },
                ),


            const SizedBox(height: 32),

            if (_isCustom) ...[
                TextField(
                  controller: _controller,
                  keyboardType: TextInputType.number,
                  style: AppTypography.display(fontSize: 22),
                  decoration: InputDecoration(
                    hintText: "personnalisé...",
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(20),
                      borderSide: BorderSide(width: 3, color: Colors.black),
                    ),
                    filled: true,
                    fillColor: AppColors.cardBg,
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide: BorderSide(
                        color: AppColors.primary,
                        width: 3,
                      ),
                    ),
                  ),
                ),
            ],

            if (_errorText != null) ...[
              const SizedBox(height: 12),
              Text(
                _errorText!,
                textAlign: TextAlign.center,
                style: AppTypography.body(
                  color: AppColors.danger,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],

            const Spacer(),
            CartoonButton(
              onPressed: () => _handlePlay(player.coins),
              color: AppColors.primary,
              shadowColor: AppColors.secondary,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const CartoonIcon(AppIcons.play, size: 26),
                  const SizedBox(width: 10),
                  const Text(
                    "JOUER",
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

Widget _buildChip({
  required String label,
  required bool isSelected,
  required VoidCallback onTap,
}) {
  return GestureDetector(
    onTap: onTap,
    child: AnimatedContainer(
      duration: const Duration(milliseconds: 150),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      decoration: BoxDecoration(
        color: isSelected ? AppColors.primary : AppColors.cardBg,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.black, width: 3),
      ),
      child: Text(
        label,
        style: AppTypography.body(
          fontSize: 15,
          fontWeight: FontWeight.w800,
          color: isSelected ? Colors.black : Colors.white,
        ),
      ),
    ),
  );
}
