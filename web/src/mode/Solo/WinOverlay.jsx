import { useEffect, useRef } from "react";
import api from "../../api"
import { FaTrophy, FaHome, FaCoins, FaStar } from "react-icons/fa";
import { HoverButton } from "../../components/assets";


let diff_coins , diff_exp

export default function WinOverlay({ level, onNext, onHome, player_data, playerSetter, sessionInfo, onRetry }) {

    

    useEffect(() => {

        async function EndLevel() {
            const res = await api.post("/game/endlevel",
                {
                    session_id: sessionInfo.session_id,
                    player_id: player_data.id,
                    ended: Math.floor(Date.now() / 1000),
                    status: "win",
                    levelPlayed : level
                });

            console.log(res.coins , player_data.coins)
            console.log(res)
            diff_coins = res.coins - player_data.coins
            diff_exp = res.xp - player_data.xp

            playerSetter(res)
            console.log(res)
        }

        EndLevel()
    }, [])

    return (
        <div className="fixed inset-0 z-50 flex flex-col gap-5 items-center justify-center bg-black/80 backdrop-filter">

            <div className="animate-pop-in border-2 backdrop-filter bg-[rgba(255,255,255,0.12)] rounded-3xl p-8 flex flex-col items-center gap-5 max-w-sm w-[90%] text-center">
                <div className="text-6xl animate-float text-amber-400"><FaTrophy /></div>
                <h2 className="font-game text-white text-3xl font-bold">Niveau {level} terminé !</h2>
                <p className="font-body text-white/70 text-sm">Tu as trouvé le nombre mystère</p>
                <div className="flex gap-3 w-full">

                    <HoverButton onClick={player_data.level === level ? onRetry : onNext}>
                        {player_data.level === level ? "Rejouer" : `Niveau ${level + 1} →`}
                    </HoverButton>

                    <button onClick={onHome}
                        className="border-2 bg-[rgba(255,255,255,0.07)] backdrop-filter font-body text-white/70 px-4 rounded-2xl hover:text-white transition-colors">
                        <FaHome className="text-3xl" />
                    </button>
                </div>
            </div>

            <div className="flex gap-4 mt-4">
                <div className="bg-linear-to-br from-amber-400 to-yellow-600 rounded-2xl p-4 flex items-center gap-3 shadow-lg">
                    <FaCoins className="text-4xl text-white drop-shadow" />
                    <div>
                        <div className="text-xs text-white/80 uppercase">Gagné</div>
                        <div className="text-3xl font-black text-white">+{diff_coins ?? '??'}</div>
                    </div>
                </div>
                <div className="bg-linear-to-br from-purple-500 to-indigo-700 rounded-2xl p-4 flex items-center gap-3 shadow-lg">
                    <div className="text-5xl font-black text-white"><FaStar /></div>
                    <div>
                        <div className="text-xs text-white/80 uppercase">XP</div>
                        <div className="text-3xl font-black text-white">+{diff_exp ?? '??'}</div>
                    </div>
                </div>
            </div>

        </div>
    )
}