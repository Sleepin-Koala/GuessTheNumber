import { useState, useEffect, useRef, useCallback  } from "react"
import api from "../../api"
import Confetti from "react-confetti";
import { useNavigate } from "react-router-dom";
import GameplayPanel from "../../components/GameplayPanel";
import WinOverlay from "./WinOverlay"
import GameOverOverlay from "./GameoverOverlay"
import StartGameOverlay from "./StartGameOverlay"
import { FaClock  , FaPause} from "react-icons/fa";
import PauseOverlay from "../../components/PauseOverlay"
import useGameSound from "../../hooks/SoundHooks";

export function TimerRing({ total, left }) {
  if (!total || total <= 0) return (
    <div className="font-body text-white/50 text-sm"><FaClock/></div>
  )
  const ratio = left / total
  const dashOffset = 283 * (1 - ratio)
  const color = ratio > 0.5 ? "#4ade80" : ratio > 0.25 ? "#fbbf24" : "#f87171"
  const urgent = ratio <= 0.25
  

  return (
    <div className="relative flex items-center justify-center" style={{ width: 72, height: 72 }}>
      <svg width="72" height="72" viewBox="0 0 100 100">
        {/* Fond du cercle */}
        <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="8" />
        {/* Arc qui se vide */}
        <circle
          cx="50" cy="50" r="45" fill="none"  
          stroke={color} strokeWidth="8"
          strokeLinecap="round"
          className="timer-ring"
          style={{
            strokeDashoffset: dashOffset,
            /* [MODIFIABLE] : transition plus rapide si tu veux un effet plus nerveux */
            transition: "stroke-dashoffset 1s linear, stroke 0.5s ease",
          }}
        />
      </svg>
      {/* Chiffre au centre */}
      <div
        key={left} // key change → re-déclenche l'animation à chaque seconde
        className={`animate-count-tick absolute font-game font-bold text-xl ${urgent ? "text-red-400" : "text-white"}`}
        style={{ textShadow: urgent ? "0 0 12px rgba(248,113,113,0.8)" : "none" }}
      >
        {left}
      </div>
    </div>
  )
}


export default function Level({ playerData, playerSetter, current_level, setLevelPlaying }) {

  const [localNumber, setLocalNumber] = useState("");
  const [hint, setHint] = useState("")
  const [gameOver, setGameOver] = useState(null)
  const [won, setWon] = useState(false)
  const [timeLeft, setTimeLeft] = useState(null)
  const [numbers, setNumbers] = useState([])
  const [gameEnded, setGameEnded] = useState(false)
  const [session, setSessionData] = useState(null)
  const [distance, setDistance] = useState(null)
  const [isReady, setReady] = useState(false)
  // ingame temporaire
  const [isShaking, setIsShaking] = useState(false)
  const [showConfetti, setShowConfetti] = useState(false);
  // others
  const timerRef = useRef(null)
  const navigate = useNavigate()
  const [isPaused , setIsPaused] = useState(false)

  const {inGameSound} = useGameSound()



  function AttemptsBar({ max, left }) {
    if (!max) return null;
    return (
      <div className="flex gap-2 items-center bg-black/30 backdrop-blur-sm rounded-full px-3 py-1.5">
        {Array.from({ length: max }).map((_, i) => (
          <div
            key={i}
            className="rounded-full transition-all duration-300"
            style={{
              width: 12,
              height: 12,
              background: i < left ? "#3b82f6" : "rgba(255,255,255,0.4)",
              boxShadow: i < left ? "0 0 8px rgba(59,130,246,0.8)" : "none",
              transform: i < left ? "scale(1)" : "scale(0.85)",
            }}
          />
        ))}
        <span className="font-mono text-white text-sm font-bold ml-1">
          {left}/{max}
        </span>
      </div>
    );
  }

  async function onGuessr() {
    if (gameEnded || !session.session_id || !parseInt(localNumber)) return;
    try {
      const res = await api.post("/game/guess", { session_id: session.session_id, player_id: playerData.id, number: parseInt(localNumber) });
      setSessionData({ ... session, attempt_left: res.attempt_left })
      setHint(res.result);
      setDistance(res.distance);

      // Gestion du résultat
      if (res.result === "OK") {
        setGameEnded(true);
        setShowConfetti(true);
        setWon(true)
        setTimeout(() => setShowConfetti(false), 4000);

      }

      if (res.attempt_left == 0) {
        setGameOver("attempts")
        setGameEnded(true);
        return
      }

      else if (res.result === "PLUS") {
        setNumbers(prev => [...prev, [parseInt(localNumber), res.result]])
        setIsShaking(true)
        inGameSound.isFalse()
      } else if (res.result === "MOINS") {
        setNumbers(prev => [...prev, [parseInt(localNumber), res.result]])
        setIsShaking(true)
        inGameSound.isFalse()
      }


      setLocalNumber("")


    } catch (error) {
      console.error(error);
    }
  }

  function GameScreen() {
    return (
      <main className="flex flex-1 flex-col items-center justify-center">

        <div className="flex w-screen justify-between flex-wrap gap-4 items-center px-4 z-10">
          {/* Tentatives */}
          <div className="flex flex-col items-center gap-1.5">
            <span className="font-black  text-white text-xs uppercase tracking-wider">Essais</span>
            <AttemptsBar max={session?.max_attempt} left={session?.attempt_left} />
          </div>

          <div className="bg-linear-to-r from-blue-500 to-purple-500 px-6 py-2 rounded-full shadow-lg border border-white/30">
            <span className="text-white font-black text-2xl tracking-wider drop-shadow-md">
              NIVEAU {current_level}
            </span>
          </div>

          <TimerRing total={session?.time_limit} left={timeLeft ?? session?.time_limit} />
        </div>

        <div className="flex flex-1 w-screen justify-center items-center">

          <GameplayPanel hint={hint} distance={distance} numbers={numbers} isShaking={isShaking}
            range={10 * Number(current_level)} localNumber={localNumber}
            onGuessr={onGuessr} NumberSetter={setLocalNumber} attempt={numbers.length} 
            onPause={HandlePause} disabled={isPaused}/>
        </div>

        {!isReady && <StartGameOverlay level={current_level}
          onStart={() => setReady(true)}
          onCancel={() => setLevelPlaying(null)} />}

        {isPaused && <PauseOverlay onResume={HandlePause}
          onRestart={handleRetry}
          onQuit={()=>navigate("/")} />}

      </main>
    )
  }

  function HandlePause(){
    if (!isPaused) setIsPaused(!isPaused)
    else setIsPaused(!isPaused)
  }

  const reset = useCallback(() => {
    setGameOver(null)
    setWon(false)
    setHint("")
    setLocalNumber("")
    setTimeLeft(null)
    setNumbers([])
    setGameEnded(false) 
  }, [])

  function handleRetry() {
    reset()
    setReady(false)
  }


  useEffect(()=>{
    if (gameOver)  inGameSound.onLose()
  } , [gameOver])

  useEffect(()=>{
    if (won)  inGameSound.onWin()
  } , [won])

  useEffect(() => {
    let t = setTimeout(() => setIsShaking(false), 350)
    return () => clearTimeout(t)
  }, [isShaking])

  useEffect(() => {
    let t = setTimeout(() => setHint(""), 2000)
    return () => clearTimeout(t)
  }, [hint])

  useEffect(() => {
    numbers.length > 5 ? setNumbers(numbers.slice(1)) : null
  }, [numbers])

  useEffect(() => {

    async function grab_level() {
      const res = await api.post("/game/level", { level: Number(current_level), player_id: playerData.id })
      setSessionData(res)

      if (res.time_limit && res.time_limit > 0) {
        setTimeLeft(res.time_limit)
      }
    }

    reset()
    isReady ? grab_level() : null

  }, [current_level, isReady])




  useEffect(() => {
    if (timeLeft === null || won || gameOver || isPaused) return
    if (timeLeft <= 0) {
      setGameOver("time")
      return
    }

    timerRef.current = setTimeout(() => setTimeLeft(t => t - 1), 1000)
    return () => clearTimeout(timerRef.current)

  }, [timeLeft, won, gameOver ,isPaused])

  return (

    <>
      {won && (
        <WinOverlay
          level={Number(current_level)}
          onNext={() => { setLevelPlaying(Number(current_level) + 1); setWon(false) ; setReady(false)}}
          onHome={() => setLevelPlaying(null)}
          player_data={playerData}
          playerSetter={playerSetter}
          sessionInfo={session}
          onRetry={handleRetry}
        />
      )}
      {gameOver && (
        <GameOverOverlay
          playerSetter={playerSetter}
          sessionInfo={session}
          player_data={playerData}
          reason={"gameover"}
          level={current_level}
          onRetry={handleRetry}
          onHome={() => setLevelPlaying(null)}
        />
      )}
      {showConfetti && <Confetti recycle={false} numberOfPieces={300} gravity={0.2} />}

      <GameScreen />

    </>
  );
}