import { useEffect, useState, useRef } from "react";
import { startAccount } from "./api/account"
import PlayerProps from "./components/PlayerProps"
import SettingsPage from "../src/assets/settings"
import { Carousel } from "./components/Carrousel";
import Bg from "./components/HomeBackdrop"
import { useNavigate } from "react-router-dom";
import useGameSound from "./hooks/SoundHooks"


const CTA = { discovery: "Apprendre", classic: "Jouer", duel: "Affronter", endless: "Tenter", settings: "Régler", sells: "Ouvrir", statictics: "Voir" }

function Home() {
  const [showSettings, setShowSettings] = useState(false);
  const [player, setPlayer] = useState({ name: null, id: null, coins: null, gems: null, xp: null, level: null })
  const navigate = useNavigate()
  const { inGameSound , mainMusic} = useGameSound()
  const isMainSoundPlayed = useRef(false)


  useEffect(() => {
    startAccount().then((p) => p && setPlayer(p))



  }, [])

  // useEffect(()=>{
  //   if (!isMainSoundPlayed.current) {mainMusic.play() }
  // } , [mainMusic])



  return (
    <>
      <Bg />
      <div className="flex flex-col h-dvh w-full">

        <PlayerProps coins={player.coins} gems={player.gems} xp={player.xp} name={player.name} level={player.level} />

        <div className="flex flex-col flex-1 items-center justify-center overflow-hidden">

          <Carousel
            itemsPerView={3}
            itemWidth={320}
            gap={20}
            onEnter={(e) => e.path == "/settings" ? setShowSettings(true) : navigate(e.path)}
            renderItem={(cat, idx) => (
              <div
                className={`rounded-3xl cursor-pointer bg-linear-to-br ${cat.color} border-4 border-white/50 transition-all duration-200 h-full`}
                onClick={() => {
                  inGameSound.click()
                  cat.id === "settings" ? setShowSettings(true) : navigate(cat.path);
                }}
              >
                <div className="candy-gloss candy-lip relative h-full rounded-[inherit] p-4 sm:p-6 flex flex-col items-center justify-center gap-2 sm:gap-3 text-center">
                  <span className="grid place-items-center w-20 h-20 sm:w-28 sm:h-28 rounded-full bg-white/20 ring-4 ring-white/40 shadow-[inset_0_-6px_0_rgba(0,0,0,.18)] animate-float-slow [@media(max-height:520px)]:hidden">
                    <cat.icon className="text-5xl sm:text-7xl drop-shadow-lg text-white" />
                  </span>
                  <h2 className="text-2xl sm:text-4xl text-white drop-shadow-md">{cat.name}</h2>
                  <p className="text-white/90 text-sm sm:text-xl font-bold leading-snug max-w-[22rem]">{cat.description}</p>
                  <span className="mt-1 sm:mt-2 inline-flex items-center justify-center min-h-11 px-6 rounded-full bg-white text-black font-game text-lg shadow-[0_4px_0_rgba(0,0,0,.3)]">{CTA[cat.id]}</span>
                  
                </div>
              </div>
            )}
          />

        </div>

        {/*Parametre*/}
        {showSettings && <SettingsPage settingsSetter={setShowSettings} player={player} playerSetter={setPlayer} />}

      </div>
    </>
  )

}

export default Home