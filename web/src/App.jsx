import { Route, Routes, BrowserRouter } from "react-router-dom";

import Home from "./Home"
import Discovery from "./mode/Discovery/main";
import Classic from "./mode/Solo/main";
import Duel from "./mode/Duel/main";
import Shop from "./mode/boutique/main.jsx"
import Stat from "./mode/stats/main.jsx"

export default function App(){
  
  return (
      <BrowserRouter>
        <Routes>
          <Route path="/" element = {<Home/>}/>
          <Route path="/discovery" element = {<Discovery/>}/>
          <Route path="/classic" element = {<Classic/>}/>
          <Route path="/duel" element = {<Duel/>}/>
          <Route path="/shop" element = {<Shop/>}/>
          <Route path="/stats" element = {<Stat/>}/>
        </Routes>
      </BrowserRouter>
  )
}





