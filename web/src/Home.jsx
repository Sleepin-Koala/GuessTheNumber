import { useEffect, useState, useRef } from "react";
import api from "./api/index" // les requetes api 
import PlayerProps from "./components/PlayerProps"
import SettingsPage from "../src/assets/settings"
import { Carousel } from "./components/Carrousel";
import Bg from "./components/Background"
import { useNavigate } from "react-router-dom";
import useGameSound from "./hooks/SoundHooks"


function Home() {
  const [showSettings, setShowSettings] = useState(false);
  const [player, setPlayer] = useState({ name: null, id: null, coins: null, gems: null, xp: null, level: null })
  const navigate = useNavigate()
  const { inGameSound , mainMusic} = useGameSound()
  const isMainSoundPlayed = useRef(false)


  useEffect(() => {
    let player_id = localStorage.getItem("id")

    async function new_player() {
      const playerid = await api.get("/user/new_player")
      localStorage.setItem("id", playerid.id)
      setPlayer(playerid)
    }

    async function get_player() {
      try {
        const player_data = await api.get(`/user/${player_id}`)
        setPlayer(player_data)
      }
      catch (e) {
        new_player()
      }
    }

    get_player();



  }, [])

  // useEffect(()=>{
  //   if (!isMainSoundPlayed.current) {mainMusic.play() }
  // } , [mainMusic])



  return (
    <>
      <Bg />
      <div className="flex flex-col h-screen w-screen">

        <PlayerProps coins={player.coins} gems={player.gems} xp={player.xp} name={player.name} />

        <div className="flex flex-col flex-1 items-center justify-center overflow-hidden">

          <Carousel
            itemsPerView={3}
            itemWidth={320}
            gap={20}
            onEnter={(e) => e.path == "/duel" ? null : e.path == "/settings" ? setShowSettings(true) : navigate(e.path)}
            renderItem={(cat, idx) => (
              <div
                className={`rounded-3xl shadow-2xl overflow-hidden cursor-pointer bg-linear-to-br ${cat.color} border-4 border-white/50 transition-all duration-200 h-full`}
                onClick={() => {
                  inGameSound.click()
                  if (cat.id === "duel") return;
                  cat.id === "settings" ? setShowSettings(true) : navigate(cat.path);
                }}
              >
                <div className="p-6 flex flex-col items-center text-center">
                  <cat.icon className="text-9xl mb-4 drop-shadow-lg  text-white " />
                  <h2 className="text-3xl font-extrabold text-white drop-shadow-md">{cat.name}</h2>
                  <p className="text-white text-2xl  font-extrabold mt-3 leading-relaxed">{cat.description}</p>
                  {cat.id === "duel" && (
                    <div className="absolute inset-0 bg-black/60 flex items-center justify-center rounded-3xl">
                      <span className="bg-white text-black px-4 py-2 rounded-full font-bold">🚧 Bientôt</span>
                    </div>
                  )}
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