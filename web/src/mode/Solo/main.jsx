import { useState , useEffect  , useRef} from "react";
import api from "../../api/index"
import BG from "../../components/Background"
import "../../index.css"
import Bar from "../../components/PlayerProps"
import Level from "./Level" 
import SelectionScreen from"./SelectionScreen"




export default function Classic() {
    const [player, setPlayer] = useState({name: null,id: null,coins: null,gems: null,xp: null,level: null})
    const [currentLevel , setCurrentLevel] = useState(null)
    
    useEffect(() => {
            const player_id = localStorage.getItem("id");
            async function get_player(){
                const player_data = await api.get(`/user/${player_id}`)
                setPlayer(player_data)
            }
            player_id ? get_player() : console.log("erreur")
    
    }, []);
    
    return (
        <>
        <BG/>
        <div className="h-screen w-screen flex flex-col">
            <Bar coins={player.coins} gems = {player.gems} xp = {player.xp} name = {player.name}/>

            {!currentLevel && <SelectionScreen player={player} onSelect={setCurrentLevel}/>}

            {currentLevel && 
            <Level playerData = {player} 
                playerSetter = {setPlayer} 
                current_level = {currentLevel} 
                setLevelPlaying = {setCurrentLevel} 
            />
            }
        </div>
        </>
    )
}