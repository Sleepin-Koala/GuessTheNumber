import { motion } from "framer-motion";
import { FaCoins, FaLock, FaCheck, FaBolt, FaHourglassHalf, FaGem, FaHeart } from "react-icons/fa";
import { GiCrystalEye } from "react-icons/gi";


// Mapping des icônes selon le type de power-up (à adapter à tes données)
const getIcon = (name) => {
  const lower = name.toLowerCase();
  if (lower.includes("temps") || lower.includes("time")) return <FaHourglassHalf />;
  if (lower.includes("indice") || lower.includes("hint")) return <GiCrystalEye />;
  if (lower.includes("vie") || lower.includes("life")) return <FaHeart />;
  return <FaBolt />; // Défaut
};

export default function ShopCard({ item, isAffordable, onBuy }) {

  return (
    <motion.div
      whileHover={{ y: -5, rotate: 1 }}
      whileTap={{ scale: 0.95 }}
      className={`bg-white border-black py-5 px-1 rounded-2xl shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]
      ${isAffordable
          ? 'bg-white border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]'
          : 'bg-slate-800 border-slate-600 shadow-none grayscale cursor-not-allowed'
        }`}
    >


      <div className="flex flex-col items-center gap-2 text-center">
        <div className={`w-16 h-16 rounded-xl flex items-center justify-center text-3xl mb-2 border-2
                    ${isAffordable ? 'bg-yellow-100 border-yellow-400 text-yellow-600' : 'bg-slate-700 border-slate-600 text-slate-500'}`}>
          {getIcon(item.name)}
        </div>
        <h3 className="font-black  text-amber-950 text-xl uppercase text-white-800 leading-tight">
          {item.name}
        </h3>
      </div>

      <p className="text-xs text-gray-500 font-semibold text-center grow">
        {item.description}
      </p>

      <div className="flex flex-col gap-2 mt-2">
        <div className="flex items-center justify-center gap-1 font-bold text-gray-800 bg-gray-100 py-1 rounded-lg border border-gray-200">
          <FaCoins className="text-yellow-500" />
          <span className="text-lg">{item.price}</span>
        </div>

        <button
          disabled={!isAffordable}
          className={`
            w-full py-2 rounded-xl font-game font-black uppercase text-sm border-b-4 transition-all
            flex items-center justify-center gap-2
            ${isAffordable
              ? 'bg-linear-to-b from-yellow-400 to-yellow-500 text-black border-yellow-700 active:border-b-0 active:translate-y-1 hover:brightness-110'
              : 'bg-slate-600 text-slate-400 border-slate-800'
            }`}
            onClick={onBuy}
            
        >
          {!isAffordable ? (
            <>
              <FaLock /> Pas assez
            </>) : "ACHETER"
          }
        </button>
      </div>

    </motion.div>
  );
}