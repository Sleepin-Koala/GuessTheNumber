import { useState, useEffect, useRef } from "react";
import api from "../../api/index"
import BG from "../../components/Background"
import "../../index.css"
import Bar from "../../components/PlayerProps"
import Game from "./game";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion"
import Tutorial from "./Tutorial";
import { Toggle , CustomSlider, CartoonButton } from "../../components/assets";
import useGameSound from "../../hooks/SoundHooks";


export default function Discover() {
  const navigate = useNavigate()
  const [currentState, setCurrentState] = useState("not_begin");
  const [maxRange, setMaxRange] = useState(50)
  const [player, setPlayer] = useState({ name: null, id: null, coins: null, gems: null, xp: null, level: null })
  const [session, setSession] = useState({ session_id: null, max_attempt: null, attempt_left: null, time_limit: null });
  const [showTutorial, setShowTutorial] = useState(false);
  const [tutorialStep, setTutorialStep] = useState(1);
  const {inGameSound} = useGameSound()


  async function StartGame() {
    try {
      if (parseInt(maxRange)) {
        const sessionData = await api.post("/game/discover", { player_id: player.id, max_range: parseInt(maxRange) });
        setSession(sessionData);
        setCurrentState("begin");
      }
    } catch (error) {
      console.error(error);
    }
  }

  useEffect(() => {
    const player_id = localStorage.getItem("id");

    async function get_player() {
      const player_data = await api.get(`/user/${player_id}`)
      setPlayer(player_data)
    }

    player_id ? get_player() : console.log("erreur")

  }, []);

  const HandleInputChange = (e) => {
    let val = parseInt(e.target.value, 10);
    if (isNaN(val)) val = 1;
    val = Math.min(1000, Math.max(1, val));
    setMaxRange(val);
  };

  function onPlay() {
    inGameSound.click()
    showTutorial ?  setCurrentState("tuto") : StartGame()
  }

  function onComplete(){
    localStorage.setItem("discover_tutorial_seen" , true)
    StartGame()
  }

  return (
    <>
      <BG />
      <div className="flex flex-col w-screen h-screen">
        <Bar coins={player.coins} gems={player.gems} xp={player.xp} name={player.name} />

        {currentState === "not_begin" &&
          <motion.div
            className="flex-1 flex flex-col justify-center items-center gap-8 z-10 px-4"
          >
            <div className="flex flex-col backdrop-blur-md bg-white/10 p-6 rounded-3xl gap-3">
              <h1 className="text-3xl font-black text-white">Selectionner le niveau</h1>
              <div className="text-white text-xl mb-2 text-center">Entre 1 et {maxRange}</div>

              <CustomSlider value = {maxRange} onChange={HandleInputChange}/>
              
              <Toggle current={showTutorial} setCurrent={setShowTutorial}>afficher l'aide</Toggle>

            </div>

            <div className="flex gap-6 flex-wrap justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onPlay}
                className="relative px-10 py-4 bg-linear-to-r uppercase from-yellow-400 to-orange-500 text-3xl font-black rounded-2xl shadow-hard hover:shadow-xl transition-all disabled:opacity-50"
              >
                jouer
                <span className="absolute top-1 left-4 w-12 h-1 bg-white/50 rounded-full" />
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => {navigate("/") ; inGameSound.click()}}
                className="px-8 py-3 bg-white/10 backdrop-blur text-white text-xl font-bold rounded-2xl border border-white/30 hover:bg-white/20"
              >
                ← QUITTER
              </motion.button>
            </div>
          </motion.div>
        }

        {currentState === "tuto" &&
          <Tutorial step = {tutorialStep} onSkip={() => setCurrentState("begin")} setStep={(i)=>setTutorialStep(i)}
          onComplete = {onComplete} />}


        {currentState === "begin" &&
          <Game session={session} stateHandler={setCurrentState} PlayerId={player.id} range={maxRange} />
        }


      </div>

    </>
  )
}