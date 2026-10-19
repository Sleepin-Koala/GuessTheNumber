import { useState } from "react";
import { motion, useAnimationControls } from "framer-motion";
import { FaCoins, FaLock, FaCheck, FaBolt, FaHourglassHalf, FaGem, FaHeart } from "react-icons/fa";
import { GiCrystalEye } from "react-icons/gi";
import { POWERUPS } from "../../assets/powerupMeta";


// Mapping des icônes selon le type de power-up (à adapter à tes données)
const getIcon = (name) => {
  const lower = name.toLowerCase();
  if (lower.includes("temps") || lower.includes("time")) return <FaHourglassHalf />;
  if (lower.includes("indice") || lower.includes("hint")) return <GiCrystalEye />;
  if (lower.includes("vie") || lower.includes("life")) return <FaHeart />;
  return <FaBolt />; // Défaut
};

export default function ShopCard({ item, isAffordable, onBuy, owned = 0 }) {
  const controls = useAnimationControls()
  const [floaters, setFloaters] = useState([])

  function buy() {
    onBuy()
    // la carte "rebondit" et le prix s'envole: on voit ce qui vient d'etre depense
    controls.start({ scale: [1, 1.08, 0.97, 1], rotate: [0, -2.5, 2.5, 0], transition: { duration: 0.45 } })
    const id = Date.now()
    setFloaters((f) => [...f, id])
    setTimeout(() => setFloaters((f) => f.filter((x) => x !== id)), 900)
  }

  return (
    <motion.div
      animate={controls}
      whileHover={{ y: -5 }}
      className={`candy-gloss relative h-full flex flex-col rounded-3xl p-4 border-2 transition-[filter,opacity]
      ${isAffordable
          ? 'bg-linear-to-b from-[#4b2d99] to-[#2a1560] border-white/25 candy-lip'
          : 'bg-linear-to-b from-[#2b2447] to-[#1c1733] border-white/10 saturate-50 opacity-80'
        }`}
    >
      {owned > 0 && (
        <span className="absolute top-3 right-3 px-2 py-0.5 rounded-full bg-black/50 text-yellow-200 text-sm font-bold" aria-label={`${owned} en stock`}>×{owned}</span>
      )}
      <div className="flex flex-col items-center gap-2 text-center">
        <div className={`w-16 h-16 rounded-full flex items-center justify-center text-3xl ring-4 shadow-[inset_0_-5px_0_rgba(0,0,0,.2)]
                    ${isAffordable ? 'bg-linear-to-b from-yellow-300 to-orange-400 ring-white/40 text-amber-900' : 'bg-slate-700 ring-white/10 text-slate-400'}`}>
          {POWERUPS[item.id]?.icon ?? getIcon(item.name)}
        </div>
        <h3 className="text-2xl text-white leading-tight">{item.name}</h3>
      </div>

      <p className="text-sm text-white/75 font-semibold text-center grow mt-1">
        {item.description}
      </p>

      <div className="relative flex flex-col gap-2 mt-3">
        <div className="flex items-center justify-center gap-1.5 font-black text-white bg-black/30 py-1 rounded-full">
          <FaCoins className="text-yellow-300" />
          <span className="text-lg tabular-nums">{item.price}</span>
        </div>

        {floaters.map((id) => (
          <span key={id} aria-hidden="true" className="animate-coin-rise pointer-events-none absolute left-1/2 -top-1 -translate-x-1/2 font-game text-2xl text-yellow-300 drop-shadow">
            -{item.price}
          </span>
        ))}

        <button
          disabled={!isAffordable}
          onClick={buy}
          className={`w-full min-h-11 py-2 rounded-2xl font-game text-lg transition-all flex items-center justify-center gap-2
            ${isAffordable
              ? 'bg-linear-to-b from-[#ffe066] to-[#ff9f1c] text-[#3b1d00] shadow-[0_5px_0_#b45309] active:translate-y-1 active:shadow-[0_1px_0_#b45309] hover:brightness-110'
              : 'bg-slate-700 text-slate-400 shadow-[0_5px_0_#0f172a]'
            }`}
        >
          {isAffordable ? "Acheter" : <><FaLock /> Pas assez</>}
        </button>
      </div>
    </motion.div>
  );
}
