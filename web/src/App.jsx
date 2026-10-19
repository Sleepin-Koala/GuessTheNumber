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
import SessionBanner from "./components/SessionBanner"
import AccountGate from "./components/AccountGate"

export default function App(){
  
  return (
      <MotionConfig reducedMotion="user">
      <BrowserRouter>
        <NetworkStatus />
        <SessionBanner />
        <Suspense fallback={null}>
        <Routes>
          <Route path="/" element = {<Home/>}/>
          <Route path="/discovery" element = {<AccountGate><Discovery/></AccountGate>}/>
          <Route path="/classic" element = {<AccountGate><Classic/></AccountGate>}/>
          <Route path="/duel" element = {<AccountGate><Duel/></AccountGate>}/>
          <Route path="/endless" element = {<AccountGate><Endless/></AccountGate>}/>
          <Route path="/shop" element = {<AccountGate><Shop/></AccountGate>}/>
          <Route path="/stats" element = {<AccountGate><Stat/></AccountGate>}/>
        </Routes>
        </Suspense>
      </BrowserRouter>
      </MotionConfig>
  )
}





