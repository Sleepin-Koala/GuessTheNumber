import { useEffect, useMemo, useState } from "react"
import { motion, useReducedMotion } from "framer-motion"
import { FaRedoAlt, FaHome } from "react-icons/fa"
import useGameSound from "../../hooks/SoundHooks"

// Une rangee par essai: la bande doree est la zone ou le nombre pouvait encore se cacher.
// Elle se resserre essai apres essai jusqu'au point final. C'est la "preuve" de la partie.
function narrowing(history, range) {
    let lo = 1, hi = range
    return history.map(([n, res]) => {
        if (res === "MOINS") lo = Math.max(lo, n + 1)      // MOINS = le nombre est plus grand que l'essai
        else if (res === "PLUS") hi = Math.min(hi, n - 1)
        else { lo = n; hi = n }
        return { n, res, lo, hi }
    })
}

const verdict = (tries, best) => {
    if (tries < best) return { stars: 3, line: `Sous la barre des ${best} essais : instinct ou chance.` }
    if (tries <= best + 1) return { stars: 3, line: `En coupant la zone en deux, ${best} essais suffisent toujours.` }
    if (tries <= best * 2) return { stars: 2, line: `Coupe la zone en deux à chaque essai : ${best} suffisent.` }
    return { stars: 1, line: `Essaie de couper la zone en deux : ${best} essais suffisent.` }
}

function Reel({ value, run }) {
    // le nombre defile puis se verrouille sur la valeur
    const [shown, setShown] = useState("?")
    useEffect(() => {
        if (!run) { setShown(value); return }
        let i = 0
        const t = setInterval(() => {
            i += 1
            setShown(i >= 14 ? value : Math.max(1, Math.round(value * (0.35 + Math.random() * 1.3))))
            if (i >= 14) clearInterval(t)
        }, 55)
        return () => clearInterval(t)
    }, [value, run])
    return <>{shown}</>
}

export default function DiscoveryWin({ history, range, onReplay, onHome }) {
    const reduce = useReducedMotion()
    const { inGameSound } = useGameSound()
    const target = history[history.length - 1][0]
    const tries = history.length
    const best = Math.max(1, Math.ceil(Math.log2(range + 1)))
    const v = verdict(tries, best)
    const rows = useMemo(() => narrowing(history, range), [history, range])
    const shownRows = rows.slice(-9)
    const pos = (n) => (range <= 1 ? 50 : ((n - 1) / (range - 1)) * 100)
    useEffect(() => { try { inGameSound.onWin() } catch { /* son indisponible */ } }, [])

    const confetti = useMemo(() => Array.from({ length: 26 }, (_, i) => ({
        left: Math.random() * 100, delay: Math.random() * 0.5, dur: 1.8 + Math.random() * 1.6, size: 6 + Math.random() * 8,
        color: ["#ffd23f", "#ff6b8b", "#4facfe", "#7cf29a", "#c9a7ff"][i % 5], rot: Math.random() * 360, key: i,
    })), [])

    return (
        <motion.section role="dialog" aria-labelledby="dw-title" aria-modal="true"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.35 }}
            className="fixed inset-0 z-40 overflow-y-auto bg-[radial-gradient(ellipse_at_50%_28%,#5b2a9e_0%,#2a1060_55%,#14062e_100%)] text-white">
            {!reduce && <div aria-hidden="true" className="pointer-events-none fixed inset-0 overflow-hidden">
                {confetti.map((c) => (
                    <span key={c.key} className="dw-confetti" style={{ left: `${c.left}%`, width: c.size, height: c.size * 0.45, background: c.color, animationDelay: `${c.delay + 0.9}s`, animationDuration: `${c.dur}s`, transform: `rotate(${c.rot}deg)` }} />
                ))}
            </div>}

            <div className="relative mx-auto flex min-h-full w-full max-w-md flex-col items-center gap-5 px-5 py-8">
                <h1 id="dw-title" className="font-game text-2xl text-yellow-200/90 tracking-wide">Nombre trouvé</h1>

                <motion.div initial={reduce ? false : { scale: 0.4, rotate: -8, opacity: 0 }} animate={{ scale: 1, rotate: 0, opacity: 1 }}
                    transition={{ type: "spring", stiffness: 260, damping: 15, delay: 0.15 }}
                    className="relative grid h-52 w-52 place-items-center rounded-full bg-linear-to-b from-[#ffe27a] via-[#ffc233] to-[#e8890c] shadow-[inset_0_-14px_0_rgba(0,0,0,.18),0_14px_0_rgba(0,0,0,.3),0_0_70px_rgba(255,200,60,.55)]">
                    <span aria-hidden="true" className="absolute inset-x-6 top-3 h-1/3 rounded-full bg-linear-to-b from-white/70 to-transparent" />
                    <span className="font-game text-[5.5rem] leading-none text-[#4a2200] drop-shadow-[0_3px_0_rgba(255,255,255,.55)] tabular-nums" aria-label={`Le nombre était ${target}`}>
                        <Reel value={target} run={!reduce} />
                    </span>
                </motion.div>

                <div className="flex gap-2" role="img" aria-label={`${v.stars} étoile${v.stars > 1 ? "s" : ""} sur 3`}>
                    {[0, 1, 2].map((i) => (
                        <motion.span key={i} initial={reduce ? false : { scale: 0, rotate: -50 }} animate={{ scale: 1, rotate: 0 }}
                            transition={{ delay: 1.0 + i * 0.18, type: "spring", stiffness: 420, damping: 11 }}
                            className={`text-4xl ${i < v.stars ? "text-yellow-300 drop-shadow-[0_0_10px_rgba(255,220,80,.9)]" : "text-white/20"}`}>★</motion.span>
                    ))}
                </div>

                <p className="text-center font-bold text-white/90">
                    <span className="font-game text-3xl text-white">{tries} essai{tries > 1 ? "s" : ""}</span><br />
                    {v.line}
                </p>

                <div className="w-full rounded-3xl bg-black/25 p-4 ring-1 ring-white/15">
                    <p className="mb-2 text-sm font-bold text-white/75">Où le nombre pouvait se cacher, essai après essai</p>
                    <ol className="flex flex-col gap-1.5">
                        {shownRows.map((r, i) => {
                            const left = pos(r.lo), width = Math.max(1.6, pos(r.hi) - pos(r.lo))
                            const last = i === shownRows.length - 1
                            return (
                                <li key={i} className="flex items-center gap-2">
                                    <span className="w-9 shrink-0 text-right font-game text-sm text-white/80 tabular-nums">{r.n}</span>
                                    <div className="relative h-4 flex-1 rounded-full bg-white/10">
                                        <motion.div initial={reduce ? false : { opacity: 0, scaleX: 0.2 }} animate={{ opacity: 1, scaleX: 1 }}
                                            transition={{ delay: 1.1 + i * 0.12, duration: 0.35 }} style={{ left: `${left}%`, width: `${width}%`, transformOrigin: "left" }}
                                            className={`absolute inset-y-0 rounded-full ${last ? "bg-yellow-300 shadow-[0_0_14px_rgba(255,214,70,.9)]" : "bg-linear-to-r from-cartoon-blue to-cartoon-purple"}`} />
                                        <span aria-hidden="true" style={{ left: `${pos(r.n)}%` }} className="absolute top-1/2 h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white ring-2 ring-[#2a1060]" />
                                    </div>
                                    <span className={`w-[4.5rem] shrink-0 text-xs font-bold whitespace-nowrap ${last ? "text-yellow-200" : "text-white/65"}`}>{last ? "Trouvé" : r.res === "MOINS" ? "Trop petit" : "Trop grand"}</span>
                                </li>
                            )
                        })}
                    </ol>
                    {rows.length > shownRows.length && <p className="mt-2 text-xs text-white/55">Les {shownRows.length} derniers essais sur {rows.length}.</p>}
                </div>

                <div className="mt-1 flex w-full gap-3">
                    <button type="button" onClick={onReplay}
                        className="flex min-h-14 flex-1 items-center justify-center gap-2 rounded-2xl bg-linear-to-b from-[#7cf29a] to-[#27b35a] font-game text-2xl text-[#073b1a] shadow-[0_6px_0_rgba(0,0,0,.3)] active:translate-y-0.5 focus-visible:outline-4 focus-visible:outline-white">
                        <FaRedoAlt aria-hidden="true" className="text-xl" />Rejouer
                    </button>
                    <button type="button" onClick={onHome} aria-label="Retour à l'accueil"
                        className="grid min-h-14 w-16 place-items-center rounded-2xl bg-white/12 text-2xl text-white ring-1 ring-white/25 focus-visible:outline-4 focus-visible:outline-white">
                        <FaHome aria-hidden="true" />
                    </button>
                </div>
            </div>
        </motion.section>
    )
}
