import { useState, useEffect, useRef, useCallback  } from "react"
import api from "../../api"
import Confetti from "react-confetti";
import { useNavigate } from "react-router-dom";
import GameplayPanel from "../../components/GameplayPanel";
import WinOverlay from "./WinOverlay"
import GameOverOverlay from "./GameOverOverlay"
import StartGameOverlay from "./StartGameOverlay"
import PowerUpTray from "../../components/PowerUpTray"
import useInventory from "../../hooks/useInventory"
import { ITEM, describeEffect } from "../../assets/powerupMeta"
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
  // power-ups: inventaire, ceux deja utilises dans cette partie, messages affiches, bonus choisis avant le depart
  const { items: inventory, refresh: refreshInventory } = useInventory(playerData.id)
  const [usedPowerups, setUsedPowerups] = useState([])
  const [infos, setInfos] = useState([])
  const pregame = useRef([])
  const advisorArmed = useRef(false)
  const wrongGuesses = useRef(0)

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

  async function applyPowerup(itemId, sessionId = session?.session_id) {
    try {
      const r = await api.post("/game/powerup", { session_id: sessionId, player_id: playerData.id, item_id: itemId })
      setUsedPowerups(u => [...u, itemId])
      setInfos(i => [...i, { text: describeEffect(r) }])
      if (r.kind === "attempts") setSessionData(s => ({ ...s, attempt_left: r.attempt_left, max_attempt: r.max_attempt }))
      if (r.kind === "time") setTimeLeft(t => (t ?? 0) + r.extra)
      refreshInventory()
    } catch (e) {
      setInfos(i => [...i, { text: e.message, error: true }])
    }
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

      else if (res.result === "PLUS" || res.result === "MOINS") {
        setNumbers(prev => [...prev, [parseInt(localNumber), res.result]])
        setIsShaking(true)
        inGameSound.isFalse()

        // bonus "Indice": le conseil arrive apres 3 erreurs
        wrongGuesses.current += 1
        if (advisorArmed.current && wrongGuesses.current >= 3) {
          advisorArmed.current = false
          applyPowerup(ITEM.ADVISOR, session.session_id)
        }
      }


      setLocalNumber("")


    } catch (error) {
      console.error(error);
    }
  }

  function GameScreen() {
    return (
      <main className="flex flex-1 flex-col items-center justify-center">

        <div className="flex w-full justify-between flex-wrap gap-4 items-center px-4 z-10">
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

        <div className="flex flex-1 min-h-0 w-full overflow-y-auto">

          <GameplayPanel hint={hint} distance={distance} numbers={numbers} isShaking={isShaking}
            range={10 * Number(current_level)} localNumber={localNumber}
            onGuessr={onGuessr} NumberSetter={setLocalNumber} attempt={numbers.length} 
            onPause={HandlePause} disabled={isPaused}
            infos={infos}
            tray={<PowerUpTray
              ids={advisorArmed.current ? [1, 2, 3, 5, 6, 7] : [1, 2, 3, 4, 5, 6, 7]}
              items={inventory} used={usedPowerups} onUse={applyPowerup}
              disabled={isPaused || gameEnded || !session} />}/>
        </div>

        {!isReady && <StartGameOverlay level={current_level}
          inventory={inventory}
          onShop={() => navigate("/shop")}
          onStart={(selected = []) => { pregame.current = selected; setReady(true) }}
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
    setUsedPowerups([])
    setInfos([])
    wrongGuesses.current = 0
    advisorArmed.current = false
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
      try {
        const res = await api.post("/game/classic/level", { level: Number(current_level), player_id: playerData.id })
        setSessionData(res)

        if (res.time_limit && res.time_limit > 0) {
          setTimeLeft(res.time_limit)
        }

        // bonus choisis avant le depart: "+3 essais" et "Rage" s'appliquent tout de suite, "Indice" s'arme
        const chosen = pregame.current
        pregame.current = []
        advisorArmed.current = chosen.includes(ITEM.ADVISOR)
        for (const id of [ITEM.LIFE, ITEM.MULTIPLIER]) {
          if (chosen.includes(id)) await applyPowerup(id, res.session_id)
        }
        if (advisorArmed.current) setInfos(i => [...i, { text: "Indice armé : un conseil arrivera après 3 erreurs" }])
      } catch (e) {
        // niveau verrouille / joueur inconnu: retour a la selection
        console.error(e)
        setLevelPlaying(null)
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

      {/* appel direct: <GameScreen /> serait remonte (et la scene 3D recreee) a chaque tick du chrono */}
      {GameScreen()}

    </>
  );
}