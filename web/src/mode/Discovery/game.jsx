import { useState, useEffect } from "react";
import api from "../../api/index"
import { motion } from "framer-motion"
import GameplayPanel from "../../components/GameplayPanel";
import { useNavigate } from "react-router-dom"
import PauseOverlay from "../../components/PauseOverlay";



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

            <div className={`flex flex-1 justify-center items-center overflow-hidden`}>
                <GameplayPanel
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