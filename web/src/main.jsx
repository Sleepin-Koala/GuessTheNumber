import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'



import '@fontsource/lilita-one'
import '@fontsource-variable/nunito'
import './index.css'
import App from './App.jsx'
import { ensureAccount } from './api/account'

// le compte (id + jeton) doit exister avant que les pages ne lisent localStorage
async function start() {
  try {
    await Promise.race([ensureAccount(), new Promise((resolve) => setTimeout(resolve, 4000))])
  } catch (e) {
    console.warn("Account check failed", e)      // serveur injoignable: l'appli s'affiche quand meme (mode hors ligne)
  }
  createRoot(document.getElementById('root')).render(<App />)
}

start()


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
