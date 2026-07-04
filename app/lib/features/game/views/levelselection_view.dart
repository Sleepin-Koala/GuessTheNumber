
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:lucide_icons/lucide_icons.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/CartoonButton.dart';
import '../bloc/game_cubit.dart';
import '../bloc/game_state.dart';

class LevelSelectionView extends StatefulWidget {

  const LevelSelectionView({super.key});

  @override
  State<LevelSelectionView> createState() => _LevelSelectionViewState();
}

class _LevelSelectionViewState extends State<LevelSelectionView> {
  int _currentPage = 0;
  final _levelsPerPage = 24;
  late PageController _pageController;
  int playerProgress = 1;

  @override
  void initState() {
    super.initState();
    final cubitState = context.read<GameCubit>().state;
    
    if (cubitState is GameSelection) {
      playerProgress = cubitState.player.level;
    }
    _currentPage = (playerProgress - 1) ~/ _levelsPerPage;
    _pageController = PageController(initialPage: _currentPage);
  }


  @override
  Widget build(BuildContext context) {
    final int totalPages = 9;

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              IconButton(
                icon: const Icon(LucideIcons.arrowLeft, color: Colors.white, size: 28),
                onPressed: () => context.read<GameCubit>().onMenu() ,
              ),
              const SizedBox(width: 8),
              const Text(
                'SÉLECTION DU NIVEAU',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 1,
                  shadows: [Shadow(color: Colors.black, offset: Offset(2, 2))],
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Grille des niveaux
          Expanded(
            child: PageView.builder(
            controller: _pageController,
            itemCount: totalPages,
            onPageChanged: (value) => setState(() {
              _currentPage = value;
            }),
            itemBuilder: (context, index) { return _buildGridForPage(index);}
          )),
        
          const SizedBox(height: 16),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Opacity(opacity: _currentPage > 0 ? 1.0 : 0.0,
              child: CartoonButton(onPressed: _currentPage > 0 ? (){
                _pageController.previousPage(duration: const Duration(milliseconds: 300), curve: Curves.easeInOut);
              }: (){},
              color: AppColors.cardBg,
              shadowColor: Colors.black,child: const Icon(LucideIcons.chevronLeft , color:Colors.white), )
              ),

              Opacity(opacity: _currentPage < totalPages ? 1.0 : 0.0,
              child: CartoonButton(onPressed: _currentPage < totalPages ? (){
                _pageController.nextPage(duration: const Duration(milliseconds: 300), curve: Curves.easeInOut);
              }: (){},
              color: AppColors.cardBg,
              shadowColor: Colors.black,child: const Icon(LucideIcons.chevronRight , color:Colors.white), )
              ),
            ],
          )

        ],
      ),
    );
  }


  @override
  void dispose() {
    super.dispose();
    _pageController.dispose();
    super.dispose();
  }
  



  

  Widget _buildLevelCard(BuildContext context, int level, bool isUnlocked) {
    if (!isUnlocked) {
      // Rendu d'un niveau VERROUILLÉ (Gris, pas de clic, cadenas)
      return Container(
        decoration: BoxDecoration(
          color: const Color(0xFF150B24), // Violet très sombre éteint
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: Colors.black, width: 3),
        ),
        child: const Center(
          child: Icon(
            LucideIcons.lock,
            color: Colors.white24,
            size: 32,
          ),
        ),
      );
    }



    // Rendu d'un niveau DÉBLOQUÉ (Utilise notre bouton 3D Cartoon)
    return CartoonButton(
      onPressed: () {
        context.read<GameCubit>().startNewGame(level: level);
      },
      color: AppColors.cardBg,
      shadowColor: Colors.black,
      child: Center(
        child: Text(
          '$level',
          style: const TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.w900,
            color: AppColors.primary, // Chiffres en Jaune Or
          ),
        ),
      ),
    );
  }
  
  Widget _buildGridForPage(int pageindex) {
    final int StartLevel = (pageindex * _levelsPerPage) + 1;
    

    return GridView.builder(
      physics: const BouncingScrollPhysics(),
      itemCount: _levelsPerPage,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount:4
      ),

      itemBuilder: (context , index) {
        final currentLevelInGrid =  StartLevel + index;  

        return _buildLevelCard(context, currentLevelInGrid, playerProgress >= currentLevelInGrid);

        // return CartoonButton(
        //   child: Column(
        //     mainAxisAlignment: MainAxisAlignment.center,
        //     children: [
        //       Text('$currentLevelInGrid' , style: const TextStyle(color: Color.fromARGB(255, 0, 0, 0) , fontSize: 20 , fontWeight: FontWeight.w900),),
        //     ],
        //   ),
        //   onPressed: (){context.read<GameCubit>().startNewGame(level: currentLevelInGrid);});
      
      });

  }
}