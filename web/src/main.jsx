import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'



import '@fontsource/lilita-one'
import '@fontsource-variable/nunito'
import './index.css'
import App from './App.jsx'
import { startAccount } from './api/account'

// la verification du compte demarre tout de suite mais ne retarde pas le premier affichage (voir AccountGate)
startAccount()
createRoot(document.getElementById('root')).render(<App />)


// PWA: service worker uniquement sur le build de production
if (import.meta.env.PROD && "serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").then((reg) => {
      reg?.addEventListener("updatefound", () => {
        const worker = reg.installing
        worker?.addEventListener("statechange", () => {
          // nouvelle version installee alors qu'une ancienne controle deja la page
          if (worker.state === "installed" && navigator.serviceWorker.controller) {
            window.dispatchEvent(new CustomEvent("sw-update", { detail: reg }))
          }
        })
      })
    }).catch((e) => console.warn("SW registration failed", e))
  })
}
