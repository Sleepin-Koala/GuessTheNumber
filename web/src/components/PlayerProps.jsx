import { FaCoins, FaGem, FaStar, FaShoppingCart ,FaArrowLeft} from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import { CartoonButton } from "./assets";
import useCountUp from "../hooks/useCountUp";

const MODES = { 
  shop: <div className="flex items-center justify-center gap-2">
          <FaShoppingCart /><div>Boutique</div>
        </div> 


  
}


export default function PlayerProps({ coins, gems, xp, name, level, mode = null }) {
  const navigate = useNavigate()

  return (
    <div className="relative flex justify-between gap-2 min-h-12 items-center w-full px-3 sm:px-6 pt-[max(0.75rem,env(safe-area-inset-top))] pl-[max(0.75rem,env(safe-area-inset-left))] pr-[max(0.75rem,env(safe-area-inset-right))] mb-3 pb-3 bg-black/20 backdrop-blur-sm overflow-hidden">

      {mode ? 
      
      <CartoonButton className="z-1 p-3 min-h-11 shrink-0 text-black"><div className="flex justify-center items-center"
      onClick={()=>navigate("/")}>
        <FaArrowLeft/><div>Retour</div>
      </div></CartoonButton>

      : 

      <div className="flex items-center gap-2 sm:gap-3 min-w-0">
        <div className="w-10 h-10 shrink-0 rounded-full bg-linear-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-white font-bold text-xl">
          {name?.toUpperCase()[0] || "?" }
        </div>
        <div className="min-w-0">
          <div className="text-white font-bold truncate max-w-[28vw] sm:max-w-[16rem]">{name || "Joueur"}</div>
          <div className="text-xs text-white/70">Niv. {level || 1}</div>
        </div>
      </div>}

      



      {/* Zone centrale : titre du jeu (déplacé ici) */}

      {
        mode ? <div className="hidden md:flex absolute inset-x-0 text-center text-3xl font-bold justify-center flex-col items-center pointer-events-none">{MODES[mode]}</div> :
          (<div className="hidden md:flex absolute inset-x-0 text-center flex-col justify-center items-center pointer-events-none">
            <h1 className="text-3xl font-black text-white drop-shadow-lg">+/−</h1>
            <p className="text-xs text-white/80">Choisis ton défi</p>
          </div>)
      }


      {/* Zone droite : ressources */}
      <div className="flex gap-1.5 sm:gap-4 shrink-0">
        <Badge icon={<FaCoins className="text-yellow-400" />} value={coins} />
        <Badge icon={<FaGem className="text-purple-300" />} value={gems} />
        <Badge icon={<FaStar className="text-orange-300" />} value={xp} label="XP" />
      </div>
    </div >
  );
}

function Badge({ icon, value, label }) {
  const shown = useCountUp(value)
  return (
    <div key={typeof value === "number" ? value : "loading"} className={`flex items-center gap-1 sm:gap-2 bg-black/40 backdrop-blur rounded-full px-2 py-1 text-sm sm:text-base sm:px-4 sm:py-2 border border-white/20 ${typeof value === "number" ? "animate-bump" : ""}`}>
      {icon}
      <span className="text-white font-bold tabular-nums">{value == null ? "..." : shown}</span>
      {label && <span className="hidden sm:inline text-white/60 text-xs">{label}</span>}
    </div>
  );
}