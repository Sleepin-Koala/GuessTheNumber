import { motion } from "framer-motion"
import { Suspense, lazy, useEffect, useRef, useState, useCallback } from "react"
import { FaArrowDown, FaArrowUp , FaPause, FaBackspace, FaTimes } from "react-icons/fa"
import { PiConfetti } from "react-icons/pi"
import useGameSound from "../hooks/SoundHooks"
import MysteryOrb from "./MysteryOrb"
const ThermoBulb = lazy(() => import("./ThermoBulb"))
  



export default function GameplayPanel(
    { isShaking, hint, range, localNumber, gameEnded = false, numbers,
        onGuessr, NumberSetter, onGameEnded = null, distance, attempt , onPause, tray = null, infos = [], showPause = true,
    disabled = null, mode = "classic" }) {

    const inputRef = useRef(null)
    // 0 = tres loin, 1 = tout proche; null tant qu'il n'y a pas de proposition
    const heat = hint === "OK" ? 1 : numbers.length ? Math.pow(Math.max(0, 1 - distance / Math.max(range, 1)), 2.2) : null
    const {inGameSound} = useGameSound()



    // zone de recherche: reduite a chaque indice. `numbers` est tronque par les ecrans, donc on cumule ici.
    const [zone, setZone] = useState({ lo: 1, hi: range })
    const lastSeen = useRef(null)
    useEffect(() => { setZone({ lo: 1, hi: range }); lastSeen.current = null }, [range])
    useEffect(() => {
        if (!numbers.length) { setZone({ lo: 1, hi: range }); lastSeen.current = null; return }
        const last = numbers[numbers.length - 1]
        if (last === lastSeen.current) return
        lastSeen.current = last
        const [n, res] = last
        setZone((z) => res === "MOINS" ? { ...z, lo: Math.max(z.lo, n + 1) } : res === "PLUS" ? { ...z, hi: Math.min(z.hi, n - 1) } : z)
    }, [numbers, range])
    const locked = gameEnded || !!disabled
    const coarse = typeof window !== "undefined" && window.matchMedia("(pointer: coarse)").matches
    const press = (d) => {
        const typed = localNumber === "" ? "" : String(localNumber)
        const next = typed === "0" ? d : typed + d
        if (next.length > String(range).length || Number(next) > range) return
        NumberSetter(Number(next))
    }
    const backspace = () => {
        const typed = String(localNumber)
        NumberSetter(typed.length <= 1 ? "" : Number(typed.slice(0, -1)))
    }
    // temperature de la partie: plus la zone est etroite, plus on "brule"
    const warmth = range <= 1 ? 1 : Math.min(1, Math.max(0, 1 - (zone.hi - zone.lo + 1) / range))
    const STOPS = [[0, 205, "Glacé"], [0.3, 175, "Froid"], [0.55, 48, "Tiède"], [0.78, 22, "Chaud"], [0.93, 4, "Brûlant"]]
    const stop = [...STOPS].reverse().find(([t]) => warmth >= t) ?? STOPS[0]
    const mood = { kind: stop[1] > 100 ? "ice" : "fire", label: hint === "OK" ? "Brûlant !" : stop[2], color: `hsl(${stop[1]} 95% 58%)`, from: `hsl(${stop[1] + 25} 95% 52%)` }
    const pct = (n) => (range <= 1 ? 0 : ((n - 1) / (range - 1)) * 100)

    // Focus automatique seulement avec une souris/clavier: sur telephone il ouvrirait le clavier a chaque essai
    useEffect(() => {
        if (window.matchMedia("(pointer: fine)").matches) inputRef.current?.focus()
    }, [isShaking, hint, gameEnded])

    function GuessChip({ number, status }) {

        return (
            <div className="bg-black/35 ring-1 ring-white/15 px-3 py-1 rounded-full">
                <div className={`${status == "MOINS" ? "text-rose-300" : "text-emerald-300"} font-black flex gap-1`}>
                    <span>{status == "MOINS" ? "↓" : "↑"}</span>
                    <span>{number}</span>
                </div>
            </div>
        )
    }

    const getShakeIntensity = (distance, range) => {
        if (!distance) return [0, 0, 0];
        const intensity = Math.min(20, Math.floor((distance / range) * 20));
        return [0,
            -intensity * 5, -intensity * 2,
            intensity, intensity * 2, intensity * 5,
            -intensity / 2, intensity / 2, 0];
    };

    const handleNumberChange = useCallback((e) => {
        const rawValue = e.target.value;
        if (rawValue === "") {
            NumberSetter("");
            return;
        }
        const num = Number(rawValue);
        if (!isNaN(num)) {
            NumberSetter(num);
        }
    });


    return (
        <motion.div className="m-auto min-w-[18rem] w-[92%] max-w-2xl gap-3 [@media(max-height:900px)]:gap-1.5 rounded-3xl relative flex flex-col justify-between items-center backdrop-blur-md  shadow-[0_18px_0_rgba(0,0,0,.28),0_30px_50px_rgba(0,0,0,.4)] ring-1 ring-white/20 bg-linear-to-b from-[#3a1a78]/90 to-[#170838]/95"
            animate={isShaking ? { x: getShakeIntensity(distance, range) } : null} transition={{ duration: 0.2 }}
        >

            {showPause && (            <button
                    onClick={()=>{inGameSound.click() ; onPause()}}
                    
                    className="cursor-pointer absolute left-2 top-2 sm:left-3 sm:top-3 z-10 bg-black/40 hover:bg-black/60 rounded-full p-3 text-white text-xl"
                >
                    <FaPause/>
                </button>)}
            <div className="flex bg-linear-to-b from-[#7b4bd6] to-[#4b24a0] w-full rounded-t-3xl shadow-[inset_0_-4px_0_rgba(0,0,0,.2)]" >
                <div className="flex-1">
                    <div className="flex items-center gap-3 w-full justify-center">
                        <span className="title-ingame text-xl sm:text-3xl [@media(max-height:900px)]:text-base text-white font-black uppercase py-3 [@media(max-height:900px)]:py-1.5 pl-14 pr-20 sm:p-3 text-center [@media(max-height:520px)]:text-lg [@media(max-height:520px)]:py-1">Devine le Nombre mystère</span>
                    </div>

                    <div role="status" className={`relative mx-3 mb-3 [@media(max-height:900px)]:mb-2 overflow-hidden rounded-2xl px-3 py-2.5 [@media(max-height:900px)]:py-1 text-xl sm:text-3xl [@media(max-height:520px)]:text-lg [@media(max-height:520px)]:py-1 font-bold text-white text-center backdrop-blur-md ring-1 shadow-[0_8px_24px_rgba(0,0,0,.25),inset_0_1px_0_rgba(255,255,255,.45)] transition-colors duration-300 ${hint === "MOINS" ? "bg-rose-500/35 ring-rose-200/50" : hint === "PLUS" ? "bg-emerald-400/30 ring-emerald-100/50" : hint === "OK" ? "bg-yellow-300/35 ring-yellow-100/60" : "bg-white/12 ring-white/30"}`}>
                        <span aria-hidden="true" className="pointer-events-none absolute inset-x-0 top-0 h-1/2 bg-linear-to-b from-white/25 to-transparent" />
                        <span className="relative drop-shadow-[0_2px_4px_rgba(0,0,0,.35)]">
                        {hint === "MOINS" ? <div className="flex justify-center items-center gap-1"><FaArrowDown /><div>Trop petit !</div></div> :
                            hint === "USED" ? "Nombre deja utilisé" :
                                hint === "PLUS" ? <div className="flex justify-center items-center gap-1"><FaArrowUp /><div>Trop Grand !</div></div> :
                                    hint === "OK" ? <div className="flex justify-center items-center gap-1"><PiConfetti /><div>Bravo ! Nombre trouvé !</div></div>
                                        : <span className="text-white/80 text-lg sm:text-2xl">À toi de jouer</span>}
                        </span>
                    </div>
                </div>

                <div className="absolute right-2 top-2 sm:right-10 sm:top-5 flex flex-col justify-center bg-linear-to-b from-[#ffe27a] to-[#ffb62e] px-3 py-1 shadow-[0_5px_0_rgba(0,0,0,.3)] rounded-2xl items-center text-[#4a2200]">
                    <div className="uppercase text-xs sm:text-base [@media(max-height:900px)]:hidden">essais</div>
                    <div className="text-4xl sm:text-7xl [@media(max-height:900px)]:text-3xl font-black">{attempt}</div>
                </div>
            </div>


            <MysteryOrb heat={heat} hint={hint} shaking={isShaking} fallback={
            <div className="w-28 h-28 sm:w-45 sm:h-45 [@media(max-height:700px)]:hidden rounded-full flex items-center justify-center text-5xl sm:text-7xl text-center"
                    style={{ boxShadow: `0 8px 32px rgba(0,0,0,.35), 0 0 0 4px rgba(255,255,255,.5)` }}>
                    <motion.span className="font-[1000] text-cartoon-blue fun-title"
                        animate={{
                            y: [0, -20, 10, 0],      // float up and down
                            rotate: [0, 10, 0]   // slight rotationx
                        }}
                        transition={{
                            duration: 2,         // total cycle time (matches CSS)
                            ease: "easeInOut",   // smooth easing
                            repeat: Infinity,    // loop forever
                            repeatType: "loop"   // default, ensures smooth loop
                        }}
                    >???
                    </motion.span>
                </div>
            } />

            <div className="flex gap-1 justify-center h-10">
                {numbers.map((n, idx) =>
                    (<div key={idx}><GuessChip number={n[0]} status={n[1]} /></div>))}
            </div>

            <div className="w-full px-4" role="group" aria-label={`Zone de recherche : entre ${zone.lo} et ${zone.hi}. ${mood.label}`}>
                <div className="mb-1.5 [@media(max-height:900px)]:mb-0.5 flex items-center justify-between text-sm font-bold">
                    <span className="rounded-full bg-white/10 px-2.5 py-0.5 text-white/90 ring-1 ring-white/25 backdrop-blur-sm tabular-nums">{zone.lo}</span>
                    <span className="font-game text-lg tracking-wide drop-shadow-[0_0_8px_var(--glow)]" style={{ color: mood.color, "--glow": mood.color }}>{mood.label}</span>
                    <span className="rounded-full bg-white/10 px-2.5 py-0.5 text-white/90 ring-1 ring-white/25 backdrop-blur-sm tabular-nums">{zone.hi}</span>
                </div>
                <div className="flex items-center">
                    <Suspense fallback={<span aria-hidden="true" className="-mr-3 h-11 w-11 shrink-0 rounded-full" style={{ background: mood.color }} />}>
                        <ThermoBulb kind={mood.kind} warmth={warmth} color={mood.color} />
                    </Suspense>
                    <div className="relative h-4 flex-1 overflow-hidden rounded-r-full bg-black/45 ring-1 ring-white/20"
                        style={{ backgroundImage: "repeating-linear-gradient(90deg, rgba(255,255,255,.14) 0 1px, transparent 1px 10%)" }}>
                        <motion.div className="absolute inset-y-0 rounded-full"
                            style={{ background: `linear-gradient(90deg, ${mood.from}, ${mood.color})`, boxShadow: `0 0 ${6 + warmth * 18}px ${mood.color}` }}
                            animate={{ left: `${pct(zone.lo)}%`, width: `${Math.max(2, pct(zone.hi) - pct(zone.lo))}%` }} transition={{ type: "spring", stiffness: 170, damping: 22 }} />
                    </div>
                </div>
            </div>

            {(tray || infos.length > 0) && (
                <div className="flex flex-col items-center gap-1.5 px-3 w-full" aria-live="polite">
                    {tray}
                    {infos.length > 0 && (
                        <div className="flex flex-wrap justify-center gap-1">
                            {infos.map((info, i) => (
                                <span key={i} className={`px-2 py-0.5 rounded-full text-xs sm:text-sm font-bold ${info.error ? "bg-red-500/80 text-white" : "bg-white/90 text-indigo-950"}`}>{info.text}</span>
                            ))}
                        </div>
                    )}
                </div>
            )}

            <div className="flex w-full items-stretch gap-2 px-4">
                <button type="button" onClick={backspace} disabled={locked || localNumber === ""} aria-label="Effacer le dernier chiffre"
                    className="grid w-12 shrink-0 place-items-center rounded-2xl bg-linear-to-b from-[#ff9a3c] to-[#e8630a] text-xl text-white shadow-[0_4px_0_rgba(0,0,0,.3)] active:translate-y-0.5 disabled:opacity-40 focus-visible:outline-4 focus-visible:outline-white"><FaBackspace aria-hidden="true" /></button>
                <input type="number" ref={inputRef}
                    placeholder={`entre 1 et ${range}`}
                    value={localNumber}
                    onChange={handleNumberChange}
                    onKeyDown={(ev) => { ev.key === "Enter" && !ev.repeat && onGuessr() }}
                    disabled={gameEnded || disabled}
                    readOnly={coarse} inputMode={coarse ? "none" : "numeric"}
                    className="min-w-0 flex-1 px-3 py-1.5 text-3xl sm:text-4xl text-center text-yellow-200 placeholder:text-white/35 placeholder:text-base font-black bg-black/35 ring-2 ring-white/20 focus:ring-4 focus:ring-yellow-300 focus:outline-none rounded-2xl tabular-nums" />
                <button type="button" onClick={() => NumberSetter("")} disabled={locked || localNumber === ""} aria-label="Tout effacer"
                    className="grid w-12 shrink-0 place-items-center rounded-2xl bg-white/12 text-xl text-white ring-1 ring-white/25 active:translate-y-0.5 disabled:opacity-40 focus-visible:outline-4 focus-visible:outline-white"><FaTimes aria-hidden="true" /></button>
            </div>

            <div className="grid w-full grid-cols-5 gap-1.5 px-4" role="group" aria-label="Clavier numérique">
                {["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"].map((d) => (
                    <button key={d} type="button" disabled={locked} onClick={() => press(d)}
                        className="min-h-10 [@media(max-height:900px)]:min-h-9 rounded-xl bg-white/15 font-game text-xl text-white tabular-nums ring-1 ring-white/25 shadow-[0_3px_0_rgba(0,0,0,.25)] active:translate-y-0.5 active:bg-yellow-300 active:text-[#4a2200] disabled:opacity-40 focus-visible:outline-3 focus-visible:outline-white">{d}</button>
                ))}
            </div>

            <div className="w-full px-4 pb-4 [@media(max-height:900px)]:pb-2.5">
                <button className="guess-button w-full py-3 [@media(max-height:900px)]:py-2 text-[#073b1a] bg-linear-to-b from-[#7cf29a] to-[#27b35a] text-2xl sm:text-3xl rounded-2xl font-bold shadow-[0_5px_0_rgba(0,0,0,.3)] active:translate-y-0.5 focus-visible:outline-4 focus-visible:outline-white"
                    onClick={gameEnded ? onGameEnded : onGuessr}>{hint === "OK" ? "Recommencer" : "Deviner !"}
                </button>
            </div>

        </motion.div>
    )
}