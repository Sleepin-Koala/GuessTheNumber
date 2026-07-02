import { motion } from "framer-motion";
import { FaPlay, FaRedoAlt, FaHome, FaPause } from "react-icons/fa";
import { CartoonButton } from "./assets";
import useGameSound from "../hooks/SoundHooks"





export default function PauseOverlay({ onResume, onRestart, onQuit }) {

  const { inGameSound } = useGameSound()

  const B = [
    { color: "green", text: "Reprendre", icon: <FaPlay />, click: onResume },
    { color: "blue", text: "Recommencer", icon: <FaRedoAlt />, click: onRestart },
    { color: "red", text: "Quitter", icon: <FaHome />, click: onQuit }


  ]
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm select-none"
      onClick={(e) => e.target === e.currentTarget && onResume()}
    >
      <motion.div
        initial={{ scale: 0.9, y: 30, opacity: 0 }}
        animate={{ scale: 1, y: 0, opacity: 1 }}
        exit={{ scale: 0.9, y: 30, opacity: 0 }}
        className="relative w-[90%] max-w-md bg-linear-to-br from-indigo-900 to-purple-900 rounded-3xl p-6 border-4 border-yellow-400 shadow-2xl text-center"

      >
        <h2 className="text-4xl font-black text-yellow-300 mb-6 gap-2 flex justify-center items-center"><FaPause /> <div>Pause</div></h2>
        <div className="flex flex-col gap-4">

          {B.map((item, id) => (
            <CartoonButton key={id} color={item.color} onClick={()=>{item.click();inGameSound.click()}}>
              <div className="flex items-center justify-center gap-2">
                {item.icon} {item.text}
              </div>
            </CartoonButton>
          ))}
        </div>
        <p className="text-white/50 text-xs mt-6">Clique à l'extérieur pour reprendre</p>
      </motion.div>
    </div>
  );
}