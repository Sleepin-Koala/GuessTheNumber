import { useEffect, useRef, useState } from "react";
import api from "../../api"
import { FaHome, FaCoins, FaStar, FaArrowRight, FaRedoAlt } from "react-icons/fa";
import { motion } from "framer-motion";
import useCountUp from "../../hooks/useCountUp";


export default function WinOverlay({ level, onNext, onHome, player_data, playerSetter, sessionInfo, onRetry }) {

    const [reward, setReward] = useState(null)
    const coins = useCountUp(reward?.coins ?? 0, 900)
    const xp = useCountUp(reward?.xp ?? 0, 900)
    const started = useRef(false)

    useEffect(() => {
        if (started.current) return
        started.current = true

        async function EndLevel() {
            try {
                const res = await api.post("/game/classic/end_level",
                    {
                        session_id: sessionInfo.session_id,
                        player_id: player_data.id,
                        ended: Date.now() / 1000,
                        status: "win",
                        level_played : level
                    });
                setReward(res)
                // la reponse ne contient que la recompense: on recharge le joueur
                playerSetter(await api.get(`/user/${player_data.id}`))
            } catch (e) {
                console.error(e)
            }
        }

        EndLevel()
    }, [])

    const stars = reward?.stars ?? 0
    const replay = player_data.level === level

    return (
        <motion.section role="dialog" aria-modal="true" aria-labelledby="win-title"
            className="fixed inset-0 z-50 overflow-y-auto bg-[radial-gradient(ellipse_at_50%_28%,#5b2a9e_0%,#2a1060_55%,#14062e_100%)] text-white"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.85, duration: 0.3 }}>
            <div className="mx-auto flex min-h-full w-full max-w-md flex-col items-center justify-center gap-5 px-5 py-8">
                <h1 id="win-title" className="font-game text-2xl text-yellow-200/90 tracking-wide">Niveau {level} terminé</h1>

                <motion.div initial={{ scale: 0.4, rotate: -8, opacity: 0 }} animate={{ scale: 1, rotate: 0, opacity: 1 }}
                    transition={{ type: "spring", stiffness: 260, damping: 15, delay: 1 }}
                    className="relative grid h-44 w-44 place-items-center rounded-full bg-linear-to-b from-[#ffe27a] via-[#ffc233] to-[#e8890c] shadow-[inset_0_-12px_0_rgba(0,0,0,.18),0_12px_0_rgba(0,0,0,.3),0_0_60px_rgba(255,200,60,.5)]">
                    <span aria-hidden="true" className="absolute inset-x-5 top-3 h-1/3 rounded-full bg-linear-to-b from-white/70 to-transparent" />
                    <span className="font-game text-[4.5rem] leading-none text-[#4a2200] drop-shadow-[0_3px_0_rgba(255,255,255,.55)] tabular-nums">{level}</span>
                </motion.div>

                <div className="flex items-end gap-2" role="img" aria-label={reward ? `${stars} étoile${stars > 1 ? "s" : ""} sur 3` : "Calcul de tes étoiles"}>
                    {[0, 1, 2].map((i) => {
                        const earned = reward && i < stars
                        return (
                            <motion.div key={i} initial={{ scale: 0, rotate: -40, opacity: 0 }}
                                animate={reward ? { scale: earned ? 1 : 0.8, rotate: 0, opacity: 1 } : {}}
                                transition={{ delay: 0.25 + i * 0.22, type: "spring", stiffness: 380, damping: 12 }}
                                className={`text-5xl ${i === 1 ? "mb-3" : ""} ${earned ? "text-yellow-300 drop-shadow-[0_0_12px_rgba(252,211,77,.85)]" : "text-white/20"}`}>
                                <FaStar />
                            </motion.div>
                        )
                    })}
                </div>

                <div className="grid w-full grid-cols-2 gap-3 rounded-3xl bg-black/25 p-4 ring-1 ring-white/15">
                    <div className="flex items-center gap-3">
                        <FaCoins aria-hidden="true" className="text-3xl text-yellow-300" />
                        <div><div className="text-sm font-bold text-white/70">Pièces</div><div className="font-game text-3xl tabular-nums">+{reward ? coins : "…"}</div></div>
                    </div>
                    <div className="flex items-center gap-3">
                        <FaStar aria-hidden="true" className="text-3xl text-cartoon-purple" />
                        <div><div className="text-sm font-bold text-white/70">XP</div><div className="font-game text-3xl tabular-nums">+{reward ? xp : "…"}</div></div>
                    </div>
                </div>

                <div className="flex w-full gap-3">
                    <button type="button" onClick={replay ? onRetry : onNext}
                        className="flex min-h-14 flex-1 items-center justify-center gap-2 rounded-2xl bg-linear-to-b from-[#7cf29a] to-[#27b35a] font-game text-2xl text-[#073b1a] shadow-[0_6px_0_rgba(0,0,0,.3)] active:translate-y-0.5 focus-visible:outline-4 focus-visible:outline-white">
                        {replay ? <><FaRedoAlt aria-hidden="true" className="text-xl" />Rejouer</> : <>Niveau {level + 1}<FaArrowRight aria-hidden="true" /></>}
                    </button>
                    <button type="button" onClick={onHome} aria-label="Retour à l'accueil"
                        className="grid min-h-14 w-16 place-items-center rounded-2xl bg-white/12 text-2xl ring-1 ring-white/25 focus-visible:outline-4 focus-visible:outline-white">
                        <FaHome aria-hidden="true" />
                    </button>
                </div>
            </div>
        </motion.section>
    )
}
