import 'package:app/core/theme/app_colors.dart';
import 'package:app/core/theme/app_icon.dart';
import 'package:app/core/theme/app_typography.dart';
import 'package:app/core/widgets/CartoonButton.dart';
import 'package:app/core/widgets/CartoonIcon.dart';
import 'package:app/core/widgets/cartoon_icon_button.dart';
import 'package:app/data/models/duel_room.dart';
import 'package:app/features/game/bloc/game_cubit.dart';
import 'package:app/features/game/bloc/game_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

class DuelLobbyView extends StatelessWidget {
  const DuelLobbyView({super.key});

  void _openCreateDialog(BuildContext context) {
    final currentState = context.read<GameCubit>().state;
    if (currentState is! GameDuelLobby) return;
    showDialog(
      context: context,
      builder: (_) => _CreateRoomDialog(playerCoins: currentState.player.coins),
    );
  }

  @override
  Widget build(BuildContext context) {

    final currentState = context.read<GameCubit>().state;
    if (currentState is! GameDuelLobby) return SizedBox.shrink();
    final player = currentState.player;
    final rooms = currentState.rooms;

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                CartoonIconButton(
                  size: 48,
                  child: const CartoonIcon(AppIcons.close, size: 20),
                  onPressed: () => context.read<GameCubit>().resetToHome(),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Text("ROOMS OUVERTES", style: AppTypography.display(fontSize: 22)),
                ),
              ],
            ),
            const SizedBox(height: 16),

            Expanded(
              child: rooms.isEmpty
                  ? Center(
                      child: Text(
                        "Aucune room pour l'instant.\nSois le premier à en créer une !",
                        textAlign: TextAlign.center,
                        style: AppTypography.body(color: Colors.white54),
                      ),
                    )
                  : ListView.separated(
                      itemCount: rooms.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 12),
                      itemBuilder: (context, index) {
                        final room = rooms[index];
                        return _RoomTile(
                          room: room,
                          canAfford: player.coins >= 33,
                          onTap: () => {context.read<GameCubit>().joinDuelRoom(room.room_id)},
                          
                        );
                      },
                    ),
            ),

            const SizedBox(height: 16),
            CartoonButton(
              // context.read<GameCubit>().createDuelRoom()
              onPressed: () => {_openCreateDialog(context)},
              color: AppColors.primary,
              shadowColor: AppColors.secondary,
              child: const Text("CRÉER UNE ROOM", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }
}

class _RoomTile extends StatelessWidget {
  final DuelRoom room;
  final bool canAfford;
  final VoidCallback onTap;

  const _RoomTile({required this.room, required this.canAfford, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Opacity(
      opacity: canAfford ? 1.0 : 0.5,
      child: GestureDetector(
        onTap: canAfford ? onTap : null,
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.cardBg,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.black, width: 3),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(room.room_name, style: AppTypography.body(fontSize: 16, fontWeight: FontWeight.w800)),
                    Text(
                      "Plage 1 – ${room.MaxRange}",
                      // {room.maxRange
                      style: AppTypography.body(fontSize: 12, color: Colors.white54),
                    ),
                  ],
                ),
              ),
              const CartoonIcon(AppIcons.coin, size: 20),
              const SizedBox(width: 6),
              Text(
                "${room.betAmount}",
                style: AppTypography.body(fontSize: 16, fontWeight: FontWeight.w800, color: AppColors.primary),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _CreateRoomDialog extends StatefulWidget {
  final int playerCoins;
  const _CreateRoomDialog({required this.playerCoins});

  @override
  State<_CreateRoomDialog> createState() => _CreateRoomDialogState();
}

class _CreateRoomDialogState extends State<_CreateRoomDialog> {
  TextEditingController textcontroller = TextEditingController(text: "room");
  int _betAmount = 50;
  int _maxRange = 100;

  static const List<int> _betSteps = [10, 25, 50, 100, 250, 500 ,1000];
  static const List<int> _rangeOptions = [10, 50, 100, 1000];

  @override
  void initState() {
    super.initState();
    
  }

  @override
  Widget build(BuildContext context) {
    final canAfford = widget.playerCoins >= _betAmount;
  

    return AlertDialog(
      backgroundColor: AppColors.cardBg,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: Colors.black, width: 3),
      ),
      title: Text("Créer une room", style: AppTypography.display(fontSize: 22)),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("NOM DE LA ROOM", style: AppTypography.body(fontSize: 11, color: Colors.white54, letterSpacing: 1.5)),
          TextField(style: AppTypography.body() ,controller: textcontroller, onChanged: (text) {setState(() {
            textcontroller.text = text;
          });},),
          const SizedBox(height: 8),
          Text("MISE", style: AppTypography.body(fontSize: 11, color: Colors.white54, letterSpacing: 1.5)),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: _betSteps.map((v) {
              final selected = v == _betAmount;
              return ChoiceChip(
                label: Text("$v"),
                selected: selected,
                onSelected: (_) => setState(() => _betAmount = v),
                selectedColor: AppColors.primary,
                backgroundColor: AppColors.background,
                labelStyle: AppTypography.body(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: selected ? Colors.black : Colors.white70,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                  side: const BorderSide(color: Colors.black, width: 2),
                ),
              );
            }).toList(),
          ),
          if (!canAfford) ...[
            const SizedBox(height: 8),
            Text(
              "Tu n'as pas assez de pièces (${widget.playerCoins}).",
              style: AppTypography.body(fontSize: 12, color: AppColors.danger),
            ),
          ],
          const SizedBox(height: 20),
          Text("PLAGE", style: AppTypography.body(fontSize: 11, color: Colors.white54, letterSpacing: 1.5)),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: _rangeOptions.map((v) {
              final selected = v == _maxRange;
              return ChoiceChip(
                label: Text("1-$v"),
                selected: selected,
                onSelected: (_) => setState(() => _maxRange = v),
                selectedColor: AppColors.primary,
                backgroundColor: AppColors.background,
                labelStyle: AppTypography.body(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: selected ? Colors.black : Colors.white70,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                  side: const BorderSide(color: Colors.black, width: 2),
                ),
              );
            }).toList(),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: Text("Annuler", style: AppTypography.body(color: Colors.white54)),
        ),
        TextButton(
          onPressed: canAfford
              ? () {
                  Navigator.of(context).pop();
                  context.read<GameCubit>().createDuelRoom(textcontroller.text, _betAmount , _maxRange);
                }
              : null,
          child: Text(
            "Créer",
            style: AppTypography.body(
              color: canAfford ? AppColors.primary : Colors.white24,
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
      ],
    );
  }
}
