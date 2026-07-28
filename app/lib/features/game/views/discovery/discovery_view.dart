import 'package:app/features/game/bloc/game_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_typography.dart';
import '../../../../core/theme/app_icon.dart';
import '../../../../core/widgets/cartoonIcon.dart';
import '../../../../core/widgets/cartoonButton.dart';
import '../../../../data/models/player.dart';
import '../../bloc/game_cubit.dart';
import '../../../../core/widgets/TutorielCaroussel.dart';

class DiscoveryView extends StatefulWidget {
  const DiscoveryView({super.key});

  @override
  State<DiscoveryView> createState() => _DiscoveryViewState();
}

class _DiscoveryViewState extends State<DiscoveryView> {
  bool _showingTutorial = true;

  @override
  Widget build(BuildContext context) {
    GameState state = context.read<GameCubit>().state;
    if (state is GameDiscovery) Player player = state.player;

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: _showingTutorial
            ? TutorialCarousel(
                onDone: () => setState(() =>_showingTutorial = false),
              )
            : const _RangePicker(),
      ),
    );
  }
}

class _RangePreset {
  final String label;
  final int max;
  const _RangePreset(this.label, this.max);
}

const List<_RangePreset> _presets = [
  _RangePreset("1 - 10", 10),
  _RangePreset("1 - 100", 100),
  _RangePreset("1 - 1000", 1000),
];

class _RangePicker extends StatefulWidget {
  const _RangePicker();

  @override
  State<_RangePicker> createState() => _RangePickerState();
}

class _RangePickerState extends State<_RangePicker> {
  int? _selectedPreset;
  bool _isCustom = false;
  final TextEditingController _customController = TextEditingController();
  String? _errorText;

  @override
  void initState() {
    super.initState();
    _selectedPreset = 0;
  }

  @override
  void dispose() {
    _customController.dispose();
    super.dispose();
  }

  int? get _chosenMax {
    if (_isCustom) return int.tryParse(_customController.text);
    if (_selectedPreset != null) return _presets[_selectedPreset!].max;
    return null;
  }

  void _handlePlay() {
    final max = _chosenMax;
    if (max == null || max < 2) {
      setState(() => _errorText = "Choisis un nombre entier d'au moins 2.");
      return;
    }
    context.read<GameCubit>().startDiscoveryGame(max_range: max);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          "CHOISIS TA PLAGE",
          textAlign: TextAlign.center,
          style: AppTypography.display(fontSize: 28),
        ),

        const SizedBox(height: 8),

        Text(
          "Le nombre secret sera tiré entre 1 et ta limite.",
          textAlign: TextAlign.center,
          style: AppTypography.body(fontSize: 14, color: Colors.white70),
        ),

        const SizedBox(height: 32),

        Wrap(
          alignment: WrapAlignment.center,
          spacing: 12,
          runSpacing: 12,
          children: [
            for (int i = 0; i < _presets.length; i++)
              _buildChip(
                label: _presets[i].label,
                isSelected: !_isCustom && _selectedPreset == i,
                onTap: () => setState(() {
                  _isCustom = false;
                  _selectedPreset = i;
                  _errorText = null;
                }),
              ),

            _buildChip(
              label: "Personnalisé",
              isSelected: _isCustom,
              onTap: () => setState(() {
                _isCustom = true;
                _selectedPreset = null;
                _errorText = null;
              }),
            ),
          ],
        ),

        if (_isCustom) ...[
          const SizedBox(height: 24),
          
          Row(
            children: [
              Text(
                "1  —  ",
                style: AppTypography.display(
                  fontSize: 22,
                  color: Colors.white54,
                ),
              ),
              
              Expanded(
                child: TextField(
                  controller: _customController,
                  keyboardType: TextInputType.number,
                  textAlign: TextAlign.center,
                  style: AppTypography.display(fontSize: 22),
                  decoration: InputDecoration(
                    filled: true,
                    fillColor: AppColors.cardBg,
                    hintText: "ex: 500",
                    hintStyle: AppTypography.body(color: Colors.white24),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide: const BorderSide(
                        color: Colors.black,
                        width: 3,
                      ),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide: const BorderSide(
                        color: Colors.black,
                        width: 3,
                      ),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide: BorderSide(
                        color: AppColors.primary,
                        width: 3,
                      ),
                    ),
                  ),
                  onChanged: (_) => setState(() => _errorText = null),
                ),
              ),
            ],
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
          onPressed: _handlePlay,
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
    );
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
}
