import { motion } from "framer-motion"
import { useEffect, useRef, useState, useCallback } from "react"
import { FaArrowDown, FaArrowUp , FaPause } from "react-icons/fa"
import { PiConfetti } from "react-icons/pi"
import useGameSound from "../hooks/SoundHooks"
import MysteryOrb from "./MysteryOrb"
  



export default function GameplayPanel(
    { isShaking, hint, range, localNumber, gameEnded = false, numbers,
        onGuessr, NumberSetter, onGameEnded = null, distance, attempt , onPause, tray = null, infos = [], showPause = true,
    disabled = null, mode = "classic" }) {

    const inputRef = useRef(null)
    // 0 = tres loin, 1 = tout proche; null tant qu'il n'y a pas de proposition
    const heat = hint === "OK" ? 1 : numbers.length ? Math.pow(Math.max(0, 1 - distance / Math.max(range, 1)), 2.2) : null
    const {inGameSound} = useGameSound()



    useEffect(() => {
        inputRef.current.focus()
    }, [isShaking, hint, gameEnded])

    function GuessChip({ number, status }) {

        return (
            <div className="bg-[#0f172a] px-2.5 py-1 rounded-lg">
                <div className={`${status == "MOINS" ? "text-red-500" : "text-green-500"} font-black flex gap-1`}>
                    <span>{status == "MOINS" ? "↓" : "↑"}</span>
                    <span>{number}</span>
                </div>
            </div>
        )
    }

    const getShakeIntensity = (distance, range) => {
        if (!distance) return [0, 0, 0];
        const intensity = Math.min(20, Math.floor((distance / range) * 20));
        console.log([0, -intensity, intensity, -intensity / 2, intensity / 2, 0])
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
        <motion.div className="m-auto min-w-[20rem] w-[90%] max-w-2xl gap-3 rounded-3xl relative flex flex-col justify-between items-center backdrop-blur-md  shadow-2xl border-3 border-cartoon-blue/50 bg-[rgba(255,255,255,.15)]"
            animate={isShaking ? { x: getShakeIntensity(distance, range) } : null} transition={{ duration: 0.2 }}
        >

            {showPause && (            <button
                    onClick={()=>{inGameSound.click() ; onPause()}}
                    
                    className="cursor-pointer absolute left-2 top-2 sm:left-3 sm:top-3 z-10 bg-black/40 hover:bg-black/60 rounded-full p-3 text-white text-xl"
                >
                    <FaPause/>
                </button>)}
            <div className="flex bg-cartoon-blue w-full rounded-t-3xl" >
                <div className="flex-1">
                    <div className="flex items-center gap-3 w-full justify-center">
                        <span className="title-ingame text-xl sm:text-3xl text-white font-black uppercase py-3 pl-14 pr-20 sm:p-3 text-center [@media(max-height:520px)]:text-lg [@media(max-height:520px)]:py-1">Devine le Nombre mystère</span>
                    </div>

                    <div className={`text-xl sm:text-3xl [@media(max-height:520px)]:text-lg [@media(max-height:520px)]:p-1 font-bold text-white text-center ${hint === "MOINS" ? "bg-cartoon-red" : hint === "PLUS" ? "bg-cartoon-green" : "bg-cartoon-yellow"} p-3 drop-shadow-lg`}>
                        {hint === "MOINS" ? <div className="flex justify-center items-center"><FaArrowDown /><div>Trop petit !</div></div> :
                            hint === "USED" ? "Nombre deja utilisé" :
                                hint === "PLUS" ? <div className="flex justify-center items-center"><FaArrowUp /><div>Trop Grand !</div></div> :
                                    hint === "OK" ? <div className="flex justify-center items-center gap-1"><PiConfetti /><div>Bravo ! Nombre trouvé !</div></div>
                                        : "..."}
                    </div>
                </div>

                <div className="absolute right-2 top-2 sm:right-10 sm:top-5 flex flex-col justify-center bg-cartoon-yellow px-2 py-1 ring-3 ring-black rounded-2xl items-center text-black">
                    <div className="uppercase text-xs sm:text-base">essais</div>
                    <div className="text-4xl sm:text-7xl [@media(max-height:520px)]:text-3xl font-black">{attempt}</div>
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

            <div>

                <input type="number" ref={inputRef}
                    placeholder={`entre 1 et ${range}`}
                    value={localNumber}
                    onChange={handleNumberChange}
                    onKeyDown={(ev) => { ev.key === "Enter" && onGuessr() }}
                    disabled={gameEnded || disabled}
                    className="w-full px-4 py-2.5 text-2xl sm:text-3xl text-center text-white font-black focus:outline-5 focus:outline-cartoon-blue rounded-xl" />

            </div>

            <button className="guess-button w-full py-3 text-white shadow-simple text-2xl sm:text-3xl hover:bg-cartoon-blue rounded-b-3xl font-bold"
                style={{ boxShadow: `0 6px 0 rgba(0,0,0,.25), 0 8px 24px rgba(0,0,0,.2)` }}
                onClick={gameEnded ? onGameEnded : onGuessr}>{hint === "OK" ? "Recommencer" : "Deviner !"}
            </button>


        </motion.div>
    )
}