import { FaCoins, FaGem, FaStar, FaShoppingCart ,FaArrowLeft} from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import { CartoonButton } from "./assets";

const MODES = { 
  shop: <div className="flex items-center justify-center gap-2">
          <FaShoppingCart /><div>Boutique</div>
        </div> 


  
}


export default function PlayerProps({ coins, gems, xp, name, level, mode = null }) {
  const navigate = useNavigate()

  return (
    <div className="flex justify-between min-h-12 items-center w-full px-6 mb-3 py-3 bg-black/20 backdrop-blur-sm overflow-hidden">

      {mode ? 
      
      <CartoonButton className="z-1 p-3 text-black"><div className="flex justify-center items-center"
      onClick={()=>navigate("/")}>
        <FaArrowLeft/><div>Retour</div>
      </div></CartoonButton>

      : 

      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-linear-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-white font-bold text-xl">
          {name?.toUpperCase()[0] || "?" }
        </div>
        <div>
          <div className="text-white font-bold">{name || "Joueur"}</div>
          <div className="text-xs text-white/70">Niv. {level || 1}</div>
        </div>
      </div>}

      



      {/* Zone centrale : titre du jeu (déplacé ici) */}

      {
        mode ? <div className="absolute text-center w-full text-3xl font-bold flex justify-center flex-col items-center -z-0">{MODES[mode]}</div> :
          (<div className="absolute text-center w-full flex justify-center flex-col items-center">
            <h1 className="text-3xl font-black text-white drop-shadow-lg">+/−</h1>
            <p className="text-xs text-white/80">Choisis ton défi</p>
          </div>)
      }


      {/* Zone droite : ressources */}
      <div className="flex gap-4">
        <Badge icon={<FaCoins className="text-yellow-400" />} value={coins} />
        <Badge icon={<FaGem className="text-purple-300" />} value={gems} />
        <Badge icon={<FaStar className="text-orange-300" />} value={xp} label="XP" />
      </div>
    </div >
  );
}

function Badge({ icon, value, label }) {
  return (
    <div className="flex items-center gap-2 bg-black/40 backdrop-blur rounded-full px-4 py-2 border border-white/20">
      {icon}
      <span className="text-white font-bold">{value ?? "..."}</span>
      {label && <span className="text-white/60 text-xs">{label}</span>}
    </div>
  );
}