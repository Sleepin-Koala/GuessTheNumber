import { useState, useEffect } from "react";
import api from "../../api/index"
import { motion } from "framer-motion"
import GameplayPanel from "../../components/GameplayPanel";
import { useNavigate } from "react-router-dom"
import PauseOverlay from "../../components/PauseOverlay";
import PowerUpTray from "../../components/PowerUpTray";
import useInventory from "../../hooks/useInventory";
import { describeEffect } from "../../assets/powerupMeta";



export default function Game({ stateHandler, session, PlayerId, range }) {
    const [isShaking, setIsShaking] = useState(false)
    const [localNumber, setLocalNumber] = useState("");
    const [gameEnded, setGameEnded] = useState(false);
    const [hint, setHint] = useState("");
    const [numbers, setNumbers] = useState([])
    const [attempt, setAttempt] = useState(0)
    const [distance, setDistance] = useState(0)
    const [isPaused, setIsPaused] = useState(false)
    const navigate = useNavigate()
    const { items: inventory, refresh: refreshInventory } = useInventory(PlayerId)
    const [usedPowerups, setUsedPowerups] = useState([])
    const [infos, setInfos] = useState([])

    async function applyPowerup(itemId) {
        try {
            const r = await api.post("/game/powerup", { session_id: session.session_id, player_id: PlayerId, item_id: itemId })
            setUsedPowerups(u => [...u, itemId])
            setInfos(i => [...i, { text: describeEffect(r) }])
            refreshInventory()
        } catch (e) {
            setInfos(i => [...i, { text: e.message, error: true }])
        }
    }
    



    async function onGuessr() {
        if (gameEnded || !session.session_id || !parseInt(localNumber)) return;
        try {
            const res = await api.post("/game/guess", { session_id: session.session_id, player_id: PlayerId, number: parseInt(localNumber) });
            setHint(res.result);
            setDistance(res.distance)
            setAttempt(attempt + 1)

            // Gestion du résultat
            if (res.result === "OK") {
                setGameEnded(true);
            } else if (res.result === "PLUS") {
                setNumbers([...numbers, [parseInt(localNumber), res.result]])
                setIsShaking(true)

            } else if (res.result === "MOINS") {
                setNumbers([...numbers, [parseInt(localNumber), res.result]])
                setIsShaking(true)
            }

            setLocalNumber("")


        } catch (error) {
            console.error(error);
        }
    }

    const EndGame = () => {
        if (gameEnded || isPaused) stateHandler("not_begin")
    }

    function HandlePause() {
        if (!isPaused) setIsPaused(!isPaused)
        else setIsPaused(!isPaused)
    }

    useEffect(() => {
        const intervall = setTimeout(() => setIsShaking(false), 300)

        return () => clearTimeout(intervall)
    }, [isShaking])

    useEffect(() => { numbers.length > 5 ? setNumbers(numbers.slice(1)) : null }, [numbers])

    return (
        <>

            <div className={`flex flex-1 min-h-0 overflow-y-auto`}>
                <GameplayPanel
                    infos={infos}
                    tray={<PowerUpTray ids={[1, 2, 4, 5, 6]} items={inventory} used={usedPowerups}
                        onUse={applyPowerup} disabled={isPaused || gameEnded} />}
                    isShaking={isShaking}
                    hint={hint}
                    numbers={numbers}
                    distance={distance}
                    range={range}
                    localNumber={localNumber}
                    gameEnded={gameEnded}
                    onGameEnded={EndGame}
                    onGuessr={onGuessr}
                    NumberSetter={setLocalNumber}
                    attempt={attempt}
                    onPause={HandlePause}
                    disabled={isPaused} />
            </div>

            {isPaused && <PauseOverlay onResume={HandlePause}
                onRestart={EndGame}
                onQuit={() => navigate("/")} />}

        </>
    )
}