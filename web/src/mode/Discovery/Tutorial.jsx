import { motion } from "framer-motion"
import { FaRegLightbulb , FaLongArrowAltRight } from "react-icons/fa";
import { BiSolidJoystick } from "react-icons/bi";
import { IoIosRocket } from "react-icons/io";
import { Toggle } from "../../components/assets";

const steps = [
    {
        logo: <FaRegLightbulb />,
        title: "Le but du jeu",
        description: "Un nombre mystère est choisi entre 1 et la limite que tu as définie. À toi de le deviner !",
        image: "🔍",
    },
    {
        logo: <BiSolidJoystick />,
        title: "Comment jouer ?",
        description: "Entre un nombre dans le champ, clique sur 'Valider'. Le jeu te dira 'trop haut' ou 'trop bas'. Continue jusqu'à trouver !",
        image: "⌨️",
    },
    {
        title: "Mode Découverte",
        description: "Ici, tu as un nombre illimité d'essais et aucun chrono. Prends ton temps et apprends. Des indices apparaîtront si tu galères.",
        image: "🧭",
    },
];


export default function Tutorial({ step, onSkip, setStep , onComplete }) {
    const current = steps[step - 1]


    const next = () => {
        if (step < steps.length) setStep(step + 1);
        else onComplete();
    };

    return (
        <motion.div
            onClick={(e) => e.target === e.currentTarget && onSkip()}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
        >

            <motion.div
                initial={{ scale: 0.9, y: 20 }}
                animate={{ scale: 1, y: 0 }}
                className="relative w-[90%] max-w-lg bg-linear-to-br from-indigo-900 to-purple-900 rounded-3xl p-6 border-2 border-yellow-400 shadow-2xl"
            >
                <button onClick={onSkip} className="absolute top-4 right-4 text-white/70 hover:text-white text-2xl">
                    ✕
                </button>

                <div className="flex text-3xl font-black text-yellow-300 justify-center items-center gap-3">{current.logo}<h2>{current.title}</h2></div>
                <p className="text-white text-lg text-center leading-relaxed mb-6">{current.description}</p>
                <div className="flex justify-between items-center gap-2 mt-4">
                    <div className="flex gap-1">
                        {steps.map((_, i) => (
                            <div
                                key={i}
                                className={`h-2 w-8 rounded-full transition-all ${i + 1 === step ? "bg-yellow-400 scale-110" : "bg-white/30"
                                    }`}
                            />
                        ))}
                    </div>
                    <button
                        onClick={next}
                        className="px-6 py-2 bg-yellow-400 text-purple-900 font-black rounded-full hover:scale-105 transition-transform"
                    >
                        {step === steps.length ? 
                        <div className="flex justify-center items-center gap-3"><IoIosRocket/><p>C'est parti !</p></div> :
                        <div className="flex justify-center items-center gap-3"><FaLongArrowAltRight/><p>suivant</p></div> 
                        }
                      
                    </button>
                </div>

                <p className="text-center text-white/50 text-xs mt-4">Clique en dehors pour passer le tutoriel</p>
            </motion.div>

        </motion.div>
    )
}