import { motion } from "framer-motion";
import { FaClock, FaHome } from "react-icons/fa";
import { IoMdClose } from "react-icons/io";
import api from "../../api";
import { useEffect } from "react";
import useGameSound from "../../hooks/SoundHooks";

// 🛡️ Constantes pour éviter les fautes de frappe dans les strings
export const OVERLAY_REASONS = {
  TIME: "time",
  ATTEMPTS: "attempts",
};

export default function GameOverOverlay({ reason, level, onRetry, onHome , playerSetter , sessionInfo , player_data}) {
  const isTimeOut = reason === OVERLAY_REASONS.TIME;

  // Configuration de l'animation
  const popInVariants = {
    hidden: { 
      scale: 0.5, 
      opacity: 0, 
      rotate: -10,
      y: 50 
    },
    visible: { 
      scale: 1, 
      opacity: 1, 
      rotate: 0, 
      y: 0,
      transition: {
        type: "spring",
        damping: 12, // Amortissement pour que ça ne vibre pas trop
        stiffness: 200, // Raideur pour l'effet "Pop"
      }
    },
    exit: {
      scale: 0.9,
      opacity: 0,
      transition: { duration: 0.2 }
    }
  };

  const shakeVariants = {
    hidden: { x: 0 },
    visible: {
      x: [0, -10, 10, -10, 10, 0],
      transition: {
        duration: 0.4,
        ease: "easeInOut"
      }
    }
  };


  useEffect(() => {
        async function EndLevel() {
            const res = await api.post("/game/endlevel",
                {
                    session_id: sessionInfo.session_id,
                    player_id: player_data.id,
                    ended: Math.floor(Date.now() / 1000),
                    status: "lose"
                });
            playerSetter(res)
        }

        EndLevel()
    }, [])

  const {inGameSound} = useGameSound()

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onRetry} // Ferme si on clique dehors (optionnel, UX courante)
        aria-hidden="true"
      />
      
      {/* Carte principale */}
      <motion.div
        variants={popInVariants}
        initial="hidden"
        animate="visible"
        exit="exit"
        role="dialog"
        aria-modal="true"
        aria-labelledby="game-over-title"
        className="relative z-10 w-full max-w-sm bg-slate-900 border-4 border-white shadow-[8px_8px_0px_0px_rgba(255,255,255,0.2)] rounded-2xl p-8 flex flex-col items-center gap-6 text-center overflow-hidden"
      >
        
        {/* Décoration d'arrière-plan (subtile) */}
        <div className="absolute top-0 left-0 w-full h-2 bg-linear-to-r from-yellow-500 via-yellow-500 to-yellow-500" />

        {/* Icône animée */}
        <motion.div 
          variants={shakeVariants}
          initial="hidden"
          animate="visible"
          className="p-4 bg-white/5 rounded-full border-2 border-white/10"
        >
          <div className="text-6xl text-white">
            {isTimeOut ? <FaClock className="text-orange-500 drop-shadow-[0_0_10px_rgba(249,115,22,0.5)]" /> : <IoMdClose className="text-red-500 drop-shadow-[0_0_10px_rgba(239,68,68,0.5)]" />}
          </div>
        </motion.div>

        {/* Titre et Message */}
        <div className="flex flex-col gap-1">
          <h2 id="game-over-title" className="font-game text-4xl font-extrabold text-white tracking-tight uppercase drop-shadow-md">
            {isTimeOut ? "Temps Écoulé !" : "Échec Total !"}
          </h2>
          <div className="h-1 w-12 bg-red-500 mx-auto rounded-full" />
        </div>

        {/* Score / Niveau mis en avant */}
        <div className="flex flex-col items-center">
          <span className="text-xs font-body text-gray-400 uppercase tracking-widest">Atteint</span>
          <p className="font-game text-3xl font-bold text-white">
            Niveau <span className="text-transparent bg-clip-text bg-linear-to-r from-blue-400 to-cyan-300">{level}</span>
          </p>
        </div>

        {/* Zone d'action */}
        <div className="flex gap-4 w-full mt-2">
          {/* Bouton Réessayer (Principal) */}
          <button 
            onClick={()=>{onRetry() ;inGameSound.click()} } 
            className="group relative flex-1 bg-linear-to-b from-red-500 to-red-600 hover:from-red-400 hover:to-red-500 text-white font-game uppercase text-lg py-4 px-6 rounded-xl font-bold border-b-4 border-red-800 active:border-b-0 active:translate-y-1 transition-all shadow-lg flex items-center justify-center gap-2"
          >
            <span>reesayer</span>
          </button>

          {/* Bouton Home (Secondaire) */}
          <button 
            onClick={()=>{onHome() ;inGameSound.click() }}
            aria-label="Retour à l'accueil"
            className="group relative bg-slate-800 hover:bg-slate-700 text-white/80 hover:text-white border-2 border-slate-600 hover:border-slate-500 font-body w-14 rounded-xl flex items-center justify-center transition-all shadow-md active:scale-95"
          >
            <FaHome size={20} />
          </button>
        </div>
      </motion.div>
    </div>
  );
}