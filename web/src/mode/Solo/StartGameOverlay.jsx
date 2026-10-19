import { motion } from "framer-motion";
import { useState } from "react";
import { FaFire, FaLightbulb, FaHeart, FaGift, FaRocket } from "react-icons/fa";
import { CartoonButton } from "../../components/assets";
import useGameSound from "../../hooks/SoundHooks";

// Chaque bonus consomme un objet de l'inventaire (ids de la boutique)
const bonusList = [
  { id: 3, icon: <FaHeart />, label: "+3 essais", description: "Trois essais de plus" },
  { id: 4, icon: <FaLightbulb />, label: "Indice", description: "Un conseil après 3 erreurs" },
  { id: 8, icon: <FaFire />, label: "Rage", description: "Pièces x2 si tu gagnes" },
];

export default function GamePreparationOverlay({ level, onStart, onCancel, inventory = {}, onShop }) {
  const [selectedBonuses, setSelectedBonuses] = useState([]);
  const { inGameSound } = useGameSound()


  const toggleBonus = (bonusId) => {
    setSelectedBonuses(prev =>
      prev.includes(bonusId) ? prev.filter(id => id !== bonusId) : [...prev, bonusId]
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && onCancel()}
    >
      <motion.div
        initial={{ scale: 0.9, y: 30 }}
        animate={{ scale: 1, y: 0 }}
        className="relative w-[90%] max-w-lg bg-linear-to-br from-indigo-900 to-purple-900 rounded-3xl p-6 border-2 border-yellow-400 shadow-2xl"
      >
        <button onClick={onCancel} className="absolute top-3 right-4 text-white/70 text-2xl">✕</button>

        <div className="text-center">
          <h2 className="text-4xl font-black text-yellow-300">Niveau {level}</h2>
          <p className="text-white text-xl mt-2">
            Devine un nombre entre <span className="font-bold text-yellow-200">1 et {level * 10}</span>
          </p>
        </div>

        <div className="mt-6">
          <div className="flex gap-2 items-center justify-center text-2xl font-semibold mb-3 text-white"><FaGift /><p> Bonus disponibles :</p></div>
          <div className="flex flex-wrap justify-center gap-4">
            {bonusList.map(b => {
              const owned = inventory[b.id] ?? 0
              return (
                <button
                  key={b.id}
                  type="button"
                  disabled={owned === 0}
                  aria-pressed={selectedBonuses.includes(b.id)}
                  onClick={() => toggleBonus(b.id)}
                  className={`relative rounded-2xl p-3 w-28 text-center transition-all ${owned === 0
                      ? "bg-white/10 text-white/40 cursor-not-allowed"
                      : selectedBonuses.includes(b.id)
                        ? "bg-yellow-400 text-black scale-105 shadow-lg"
                        : "bg-white/20 text-white hover:bg-white/30"
                    }`}
                >
                  <span className="absolute -top-2 -right-2 grid place-items-center min-w-6 h-6 px-1 rounded-full bg-black text-white text-xs font-bold">×{owned}</span>
                  <div className="text-3xl flex justify-center">{b.icon}</div>
                  <div className="font-bold text-sm">{b.label}</div>
                  <div className="text-xs opacity-80">{b.description}</div>
                </button>
              )
            })}
          </div>
        </div>

        {bonusList.every(b => (inventory[b.id] ?? 0) === 0) && onShop && (
          <p className="text-center text-white/80 mt-3">Aucun bonus en stock. <button type="button" onClick={onShop} className="underline font-bold text-yellow-200 min-h-11">Va à la boutique</button></p>
        )}

        <div className="flex justify-center gap-4 mt-8">
          <CartoonButton color="green" onClick={()=> {onStart(selectedBonuses.filter(id => (inventory[id] ?? 0) > 0));inGameSound.click()}}>
            <div className="flex justify-center align-items gap-3"><FaRocket />GO !</div>
          </CartoonButton>
          <CartoonButton color="red" onClick={()=> {onCancel();inGameSound.click()}}>
            Annuler
          </CartoonButton>
        </div>
      </motion.div>
    </motion.div>
  );
}