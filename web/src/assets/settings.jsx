import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import api from "../api/index";
import { FaCog, FaUser, FaVolumeUp, FaVolumeMute, FaTimes, FaSave } from "react-icons/fa";
import { BiSolidJoystick } from "react-icons/bi"
import { Toggle } from "../components/assets";
import useGameSound from "../hooks/SoundHooks";

export default function Settings({ settingsSetter, player, playerSetter }) {
    const [soundEnabled, setSoundEnabled] = useState(() => {
        const saved = localStorage.getItem("sound");
        return saved === "true" ? true : saved === "false" ? false : true; // défaut true
    });

    const [tempUsername, setTempUsername] = useState(player.name || "");
    const {inGameSound} = useGameSound()

    const [isSaving, setIsSaving] = useState(false);

    // Sauvegarde du son dans localStorage
    useEffect(() => {
        localStorage.setItem("sound", soundEnabled);
    }, [soundEnabled]);

    const saveSettings = async () => {
        if (isSaving) return;
        setIsSaving(true);
        try {
            if (tempUsername !== player.name) {
                const res = await api.post("/user/rename", {
                    player_id: player.id,
                    name: tempUsername,
                });
                playerSetter(res);
            }
            settingsSetter(false);
        } catch (error) {
            console.error(error);
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <AnimatePresence>
            <div
                className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
                onClick={() => settingsSetter(false)}
            >
                <motion.div
                    initial={{ opacity: 0, scale: 0.8, y: 30 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.8, y: 30 }}
                    transition={{ type: "spring", damping: 20 }}
                    className="relative w-full max-w-md rounded-3xl bg-linear-to-br from-indigo-800 to-purple-900 p-6 shadow-hard border-4 border-yellow-400"
                    onClick={(e) => e.stopPropagation()}
                >
                    {/* En-tête avec icône et fermeture */}
                    <div className="flex justify-between items-center mb-6">
                        <div className="flex items-center gap-2">
                            <FaCog className="text-3xl text-yellow-300 animate-spin-slow" />
                            <h2 className="text-3xl font-black text-white drop-shadow-md">Paramètres</h2>
                        </div>
                        <button
                            onClick={() => {settingsSetter(false);inGameSound.click()}}
                            className="text-white/70 hover:text-white text-2xl p-2 rounded-full hover:bg-white/20 transition"
                        >
                            <FaTimes />
                        </button>
                    </div>

                    {/* Pseudo */}
                    <div className="mb-6">
                        <label className="flex items-center gap-2 text-white font-bold mb-2">
                            <FaUser /> Pseudo
                        </label>
                        <input
                            type="text"
                            value={tempUsername}
                            onChange={(e) => setTempUsername(e.target.value)}
                            className="w-full p-3 bg-white/20 border-2 border-white/30 rounded-xl text-white font-bold text-lg focus:outline-none focus:border-yellow-400"
                            placeholder="Ton pseudo"
                        />
                    </div>

                    <Toggle current={soundEnabled} setCurrent={setSoundEnabled}><div className="flex items-center gap-2 text-white font-bold">
                        {soundEnabled ? <FaVolumeUp className="text-green-400" /> : <FaVolumeMute className="text-red-400" />}
                        Effets sonores
                    </div> </Toggle>



                    {/* Bouton sauvegarder */}
                    <button
                        onClick={()=>{saveSettings();inGameSound.click()}}
                        disabled={isSaving}
                        className="w-full py-3 bg-linear-to-r from-yellow-400 to-orange-500 text-black font-black text-xl rounded-xl shadow-hard hover:shadow-xl transition active:scale-95 flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                        {isSaving ? "⏳" : <FaSave />}
                        Sauvegarder
                    </button>

                    {/* Petite mascotte décorative */}
                    <div className="absolute -bottom-8 -left-8 text-7xl opacity-20 pointer-events-none rotate-12">
                        <BiSolidJoystick />
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
}