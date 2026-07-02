

import { motion } from "framer-motion"
import { useEffect, useRef } from "react";

export function Toggle({ children, current, setCurrent }) {

    return (<div className="mb-5 flex justify-between items-center bg-black/30 rounded-xl p-3">
        <label className="text-gray-700 dark:text-gray-200 font-black">{children}</label>
        <button
            onClick={() => setCurrent(!current)}
            className={`w-12 h-6 rounded-full transition ${current ? "bg-green-500" : "bg-gray-400"
                } relative`}
        >
            <motion.span
                animate={current ? null : { left: 5 }}
                className="absolute top-0.5 w-5 h-5 bg-white rounded-full transition"
            />
        </button>
    </div>)
}

// export function CustomGameSlider({
//     value,
//     onChange,
//     min = 1,
//     max = 1000,
//     label = "",
//     theme = "fantasy" // Options: 'cyberpunk', 'fantasy', 'scifi'
// }) {

//     // Configuration des thèmes de jeu disponibles
//     const themes = {
//         cyberpunk: {
//             bg: "bg-black border-cyan-400",
//             track: "bg-zinc-900",
//             fill: "bg-magenta-500 shadow-[0_0_15px_#f43f5e]",
//             thumb: "bg-cyan-400 shadow-[0_0_10px_#22d3ee]",
//             text: "text-cyan-400 font-mono tracking-widest uppercase",
//         },
//         fantasy: {
//             bg: "bg-amber-950 border-amber-700 rounded",
//             track: "bg-stone-900",
//             fill: "bg-emerald-600 shadow-[inset_0_2px_4px_rgba(0,0,0,0.6)]",
//             thumb: "bg-amber-500 border-amber-300 rounded-sm",
//             text: "text-amber-200 font-serif italic",
//         },
//         scifi: {
//             bg: "bg-slate-900 border-slate-500 clip-path-panel",
//             track: "bg-slate-950",
//             fill: "bg-sky-500 animate-pulse",
//             thumb: "bg-slate-100 border-sky-400",
//             text: "text-sky-300 font-sans tracking-wider font-semibold",
//         }
//     };

//     const currentTheme = themes[theme] || themes.cyberpunk;
//     const percentage = ((value - min) / (max - min)) * 100;

//     return (
//         <div className={`w-full  ${label != "" ? "border-2 p-4" : null}   ${currentTheme.bg} transition-all duration-300`}>

//             {label != "" ? <div className={`flex justify-between text-xs mb-2 ${currentTheme.text}`}>
//                 <span>{label}</span>
//                 <span>{value} / {max}</span>
//             </div> : null}


//             <div className="relative flex items-center h-8">
//                 {/* Input invisible mais cliquable sur toute la zone */}
//                 <input
//                     type="range"
//                     min={min}
//                     max={max}
//                     value={value}
//                     onChange={onChange}
//                     className="absolute w-full h-full opacity-100 cursor-pointer z-20"
//                 />

//                 {/* Jauge visuelle personnalisée arrière-plan */}
//                 <div className={`absolute w-full h-4 ${currentTheme.track} overflow-hidden z-0`}>
//                     {/* Remplissage de la barre */}
//                     <div
//                         className={`h-full ${currentTheme.fill} transition-all duration-100`}
//                         style={{ width: `${percentage}%` }}
//                     />
//                 </div>

//                 {/* Curseur (Thumb) visuel factice calqué sur la valeur */}
//                 <div
//                     className={`absolute h-6 w-3 ${currentTheme.thumb} border pointer-events-none z-10 transition-all duration-100`}
//                     style={{
//                         left: `calc(${percentage}% - (${percentage * 0.12}px))`,
//                     }}
//                 />
//             </div>
//         </div>
//     );
// }


export function CustomSlider({ min = 1, max = 1000, value, onChange }) {

    const percentage = ((value - min) / (max - min)) * 100;
    const inputRef = useRef(null)
    let width

    useEffect(() => {
        console.log(inputRef.current.getBoundingClientRect())
        width = Math.ceil(inputRef.current.getBoundingClientRect().width)

    }, [width])

    return (
        <div className="w-full transition-all duration-300">
            <input
                type="range"
                min={min}
                max={max}
                step={10}
                value={value}
                onChange={onChange}
                className={`
                    absolute 
                    opacity-0
                    cursor-pointer
                    z-10
                    w-[90%]
                `}

            />


            <div className="relative w-full rounded-2xl h-2 bg-white/30" ref={inputRef}>

                <div className="absolute -top-2 h-6 w-6 cursor-pointer bg-amber-200 rounded-full -translate-x-1/2"
                    style={{
                        left: `${percentage}%`,
                    }}></div>
            </div>
        </div>

    )
}


export function CartoonButton({ children, onClick = null, className = "px-10 py-4 text-3xl" }) {


    return (
        <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onClick}
            className={`relative bg-linear-to-r cursor-pointer from-yellow-400 to-orange-500 font-black rounded-2xl shadow-hard hover:shadow-xl transition-all disabled:opacity-50 ${className ?? ""}`}>
            {children}
            <span className="absolute top-1 left-4 w-12 h-1 bg-white/50 rounded-full" />
        </motion.button>
    )
}




export function HoverButton({ onClick, children }) {

    return (
        <div onClick={onClick}
            className="transition-all duration-100 hover:-translate-y-0.5 hover:shadow-[0_6px_0_#1d4ed8,0_12px_28px_rgba(99,102,241,0.5)]
                    flex-1 text-white text-lg py-3 rounded-2xl font-bold
                    active:translate-y-0.5 active:shadow-[0_2px_0_#1d4ed8,0_4px_12px_rgba(99,102,241,0.3)]
                    bg-linear-to-br from-[#3b82f6] to-[#6366f1] shadow-[0_4px_0_#1d4ed8,0_8px_24px_rgba(99,102,241,0.4)]">
            {children}
        </div>
    )
}