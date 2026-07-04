import 'package:app/core/theme/app_colors.dart';
import 'package:app/features/game/bloc/game_cubit.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

class TimerBar extends StatefulWidget {
  final int maxTime;
  const TimerBar({super.key, required this.maxTime});

  @override
  State<TimerBar> createState() => _TimerBarState();
}

class _TimerBarState extends State<TimerBar>
    with SingleTickerProviderStateMixin {

  
  late AnimationController _controller;
  bool end = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: Duration(seconds: widget.maxTime),
    );

    _controller.reverse(from: 1);

    _controller.addListener(() {
      if (_controller.value == 0 && !end) {
        context.read<GameCubit>().onTimeUp();
        end = true;
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Padding(
          padding: EdgeInsetsGeometry.all(10),
          child: LinearProgressIndicator(
            value: _controller.value,
            color: AppColors.success,
            minHeight: 10,
            backgroundColor: AppColors.danger,
            borderRadius: BorderRadius.all(Radius.circular(12)),
          ),
        );
      },
    );
  }
}
