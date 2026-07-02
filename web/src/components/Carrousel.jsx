import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { GiCompass, GiGearHammer, GiShop } from "react-icons/gi";
import { FaStairs } from "react-icons/fa6";
import { GiSwordClash } from "react-icons/gi";
import { FaBullseye, FaChevronRight, FaChevronLeft } from "react-icons/fa";
import useGameSound from "../hooks/SoundHooks"

const CATEGORIES = [
    {
        id: "statictics",
        name: "Statistique",
        icon: FaStairs,
        color: "from-yellow-400 to-yellow-600",
        description: "Les informations sur tes parties.",
        buttonColor: "bg-blue-500",
        path: "/stats",
    },

    {
        id: "discovery",
        name: "Mode Découverte",
        icon: GiCompass,
        color: "from-green-400 to-emerald-600",
        description: "Apprends les règles pas à pas. Des indices t'aideront à trouver le bon nombre. Parfait pour débuter !",
        buttonColor: "bg-green-500",
        path: "/discovery",
    },
    {
        id: "classic",
        name: "Mode Classique",
        icon: FaBullseye,
        color: "from-blue-400 to-indigo-600",
        description: "Le jeu original : trouve le nombre mystère en un minimum d'essais. Chronométré et sans aide.",
        buttonColor: "bg-blue-500",
        path: "/classic",
    },
    {
        id: "duel",
        name: "Mode Duel",
        icon: GiSwordClash,
        color: "from-orange-400/20 to-red-600/20",
        description: "Affronte un autre joueur au tour par tour.",
        buttonColor: "bg-orange-500",
        path: "/duel",
    },
    {
        id: "settings",
        name: "Parametres",
        icon: GiGearHammer,
        color: "from-slate-400 to-slate-600",
        description: "Ajuste les parametres et definies tes preferences.",
        buttonColor: "bg-blue-500",
        path: "/settings",
    },
    {
        id: "sells",
        name: "Boutique",
        icon: GiShop,
        color: "from-orange-400 to-orange-600",
        description: "Achete des powers-ups et autres.",
        buttonColor: "bg-blue-500",
        path: "/shop",
    },
    {
        id: "statictics",
        name: "Statistique",
        icon: FaStairs,
        color: "from-yellow-400 to-yellow-600",
        description: "Les informations sur tes parties.",
        buttonColor: "bg-blue-500",
        path: "/stats",
    },
    {
        id: "discovery",
        name: "Mode Découverte",
        icon: GiCompass,
        color: "from-green-400 to-emerald-600",
        description: "Apprends les règles pas à pas. Des indices t'aideront à trouver le bon nombre. Parfait pour débuter !",
        buttonColor: "bg-green-500",
        path: "/discovery",
    },
];

const shakeVariants = {
    idle: { x: 0 },
    left: { x: [0, -12, 10, -8, 6, -4, 0], transition: { duration: 0.45 } },
    right: { x: [0, 12, -10, 8, -6, 4, 0], transition: { duration: 0.45 } },
};



export function Carousel({ renderItem, itemWidth = 300, itemsPerView = 3  , onEnter = null}) {
    const [currentIndex, setCurrentIndex] = useState(1)
    const totalItems = CATEGORIES.length;
    const maxIndex = Math.max(0, totalItems - itemsPerView);
    const [shake, setShake] = useState(null);
    const {inGame} = useGameSound()

    const getItemStyle = (index) => {

        if (currentIndex != 0 || currentIndex != totalItems - 1) {
            const diff = index - currentIndex;
            const isLeft = diff < 0;
            const absDiff = Math.abs(diff);

            // Échelle : centrale = 1, latérales = 0.8, plus éloignées = 0.6
            let scale = 1;
            let opacity = 1;
            let blur = 0;
            let translateX = 0;

            if (absDiff === 0) { scale = 1; opacity = 1; blur = 0; translateX = 0; }
            else if (absDiff === 1) { scale = 0.85; opacity = 0.8; blur = 2; translateX = isLeft ? -itemWidth * 0.4 : itemWidth * 0.4; }
            else { scale = 0.7; opacity = 0.4; blur = 4; translateX = isLeft ? -itemWidth * 0.7 : itemWidth * 0.7; }


            const zIndex = 10 - absDiff;
            return { scale, opacity, filter: `blur(${blur}px)`, x: translateX, zIndex: zIndex };
        }
        else {
            console.log("dsf")
        }
    };

    const next = () => {
        const limit = maxIndex + (itemsPerView - 2);
        // if (currentIndex >= limit) { setShake("right"); setTimeout(() => setShake(null), 500); return; }
        if (currentIndex >= limit) { setCurrentIndex(1); return; }
        setCurrentIndex((prev) => prev + 1);
    };

    const prev = () => {
        const limit = maxIndex + (itemsPerView - 2);
        // if (currentIndex <= 1) { setShake("left"); setTimeout(() => setShake(null), 500); return; }
        if (currentIndex <= 1) { setCurrentIndex(limit); return; }
        setCurrentIndex((prev) => prev - 1);
    };

    useEffect(() => {
        const handleKey = (e) => {
            if (e.key === "ArrowRight") next();
            if (e.key === "ArrowLeft") prev();
            if (e.key === "Enter") onEnter(CATEGORIES[currentIndex]);
        };
        window.addEventListener("keydown", handleKey);
        return () => window.removeEventListener("keydown", handleKey);
    }, [currentIndex]);

    return (
        <motion.div
            className="flex items-center justify-center overflow-hidden flex-1 w-full"
            variants={shakeVariants}
            animate={shake ?? "idle"}
        >

            {CATEGORIES.map((item, idx) => {
                const style = getItemStyle(idx);
                const absDiff = Math.abs(currentIndex - idx);

                if (absDiff > 1) return null;

                return (
                    <motion.div key={item.id} className="select-none"
                        animate={style}
                        style={{ width: "50%", flexShrink: 0, height: "70%" }}
                        whileHover={{ scale: 1.03 }}
                        whileTap={{ scale: 0.95 }}

                    >
                        {renderItem(item, idx)}
                    </motion.div>
                )
            }


            )}


            {/* Flèches de navigation */}
            {currentIndex == 0 ? null : <FaChevronLeft onClick={prev} className="absolute left-4 z-20 bg-white/30 backdrop-blur rounded-full p-2 text-9xl hover:bg-white/50 transition" />}
            {currentIndex == CATEGORIES.length - 1 ? null : <FaChevronRight onClick={next} className="absolute right-4 z-20 bg-white/30 backdrop-blur rounded-full p-2 text-9xl hover:bg-white/50 transition" />}
            <div className="absolute bottom-4 flex gap-2">
                {[...Array(totalItems-2)].map((_, i) => (
                    <button
                        key={i}
                        onClick={() => setCurrentIndex(i+1)}
                        className={`w-2 h-2 rounded-full transition-all cursor-pointer ${i+1 === currentIndex ? "bg-white scale-125" : "bg-white/40"}`}
                    />
                ))}
            </div>

        </motion.div>


    )
}