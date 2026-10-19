import { lazy, Suspense } from "react";
import { Route, Routes, BrowserRouter } from "react-router-dom";
import { MotionConfig } from "framer-motion";

import Home from "./Home"
const Discovery = lazy(() => import("./mode/Discovery/main"))
const Classic = lazy(() => import("./mode/Solo/main"))
const Duel = lazy(() => import("./mode/Duel/main"))
const Endless = lazy(() => import("./mode/Endless/main"))
const Shop = lazy(() => import("./mode/boutique/main.jsx"))
const Stat = lazy(() => import("./mode/stats/main.jsx"))
import NetworkStatus from "./components/NetworkStatus"

export default function App(){
  
  return (
      <MotionConfig reducedMotion="user">
      <BrowserRouter>
        <NetworkStatus />
        <Suspense fallback={null}>
        <Routes>
          <Route path="/" element = {<Home/>}/>
          <Route path="/discovery" element = {<Discovery/>}/>
          <Route path="/classic" element = {<Classic/>}/>
          <Route path="/duel" element = {<Duel/>}/>
          <Route path="/endless" element = {<Endless/>}/>
          <Route path="/shop" element = {<Shop/>}/>
          <Route path="/stats" element = {<Stat/>}/>
        </Routes>
        </Suspense>
      </BrowserRouter>
      </MotionConfig>
  )
}





