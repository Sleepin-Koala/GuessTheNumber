import { motion } from "framer-motion";
import { FaClock, FaHome, FaRedoAlt } from "react-icons/fa";
import { IoMdClose } from "react-icons/io";
import api from "../../api";
import { useEffect, useRef } from "react";
import useGameSound from "../../hooks/SoundHooks";

// 🛡️ Constantes pour éviter les fautes de frappe dans les strings
export const OVERLAY_REASONS = {
  TIME: "time",
  ATTEMPTS: "attempts",
};

export default function GameOverOverlay({ reason, level, onRetry, onHome , playerSetter , sessionInfo , player_data}) {
  const isTimeOut = reason === OVERLAY_REASONS.TIME;

  const started = useRef(false)

  useEffect(() => {
        if (started.current) return
        started.current = true

        async function EndLevel() {
            try {
                await api.post("/game/classic/end_level",
                    {
                        session_id: sessionInfo.session_id,
                        player_id: player_data.id,
                        ended: Date.now() / 1000,
                        status: "lose",
                        level_played: Number(level)
                    });
            } catch (e) {
                console.error(e)
            }
        }

        EndLevel()
    }, [])

  const {inGameSound} = useGameSound()

  const title = isTimeOut ? "Temps écoulé" : "Plus d'essais"
  const hint = isTimeOut
    ? "Le chrono a gagné cette fois. Le prochain essai se joue plus vite : coupe la zone en deux."
    : "Le nombre t'a échappé. Coupe la zone en deux à chaque essai pour le coincer."

  return (
    <motion.section role="dialog" aria-modal="true" aria-labelledby="game-over-title"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}
      className="fixed inset-0 z-50 overflow-y-auto bg-[radial-gradient(ellipse_at_50%_28%,#4a2466_0%,#1f0f3d_58%,#0d0620_100%)] text-white">
      <div className="mx-auto flex min-h-full w-full max-w-md flex-col items-center justify-center gap-5 px-5 py-8 text-center">
        <h1 id="game-over-title" className="font-game text-2xl text-rose-200/90 tracking-wide">Niveau {level} manqué</h1>

        <motion.div initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1, x: [0, -10, 10, -8, 8, 0] }}
          transition={{ scale: { type: "spring", stiffness: 240, damping: 14 }, x: { delay: 0.3, duration: 0.45 } }}
          className="relative grid h-40 w-40 place-items-center rounded-full bg-linear-to-b from-[#9a8fb5] via-[#6d6590] to-[#463f66] shadow-[inset_0_-12px_0_rgba(0,0,0,.25),0_12px_0_rgba(0,0,0,.35),0_0_50px_rgba(255,107,139,.25)]">
          <span aria-hidden="true" className="absolute inset-x-5 top-3 h-1/3 rounded-full bg-linear-to-b from-white/35 to-transparent" />
          <span className="text-7xl text-white/90 drop-shadow-[0_3px_0_rgba(0,0,0,.35)]" aria-hidden="true">
            {isTimeOut ? <FaClock /> : <IoMdClose />}
          </span>
        </motion.div>

        <div>
          <p className="font-game text-4xl">{title}</p>
          <p className="mx-auto mt-2 max-w-xs font-bold text-white/80">{hint}</p>
        </div>

        <div className="flex w-full gap-3">
          <button type="button" onClick={() => { onRetry(); inGameSound.click() }}
            className="flex min-h-14 flex-1 items-center justify-center gap-2 rounded-2xl bg-linear-to-b from-[#ff8aa5] to-[#e0405f] font-game text-2xl text-[#4a0618] shadow-[0_6px_0_rgba(0,0,0,.3)] active:translate-y-0.5 focus-visible:outline-4 focus-visible:outline-white">
            <FaRedoAlt aria-hidden="true" className="text-xl" />Réessayer
          </button>
          <button type="button" onClick={() => { onHome(); inGameSound.click() }} aria-label="Retour à l'accueil"
            className="grid min-h-14 w-16 place-items-center rounded-2xl bg-white/12 text-2xl ring-1 ring-white/25 focus-visible:outline-4 focus-visible:outline-white">
            <FaHome aria-hidden="true" />
          </button>
        </div>
      </div>
    </motion.section>
  );
}
