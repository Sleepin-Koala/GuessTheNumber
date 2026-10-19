import { useEffect, useRef, useState } from "react"
import { wsUrl } from "../api/index"
import { getToken } from "../api/account"

const HEARTBEAT_MS = 20000      // le serveur ferme une socket silencieuse au bout de 60 s
const NO_RETRY = [4401, 4403, 4404]   // pas authentifie / pas membre / salle inconnue: reessayer ne servirait a rien

/**
 * WebSocket qui se reconnecte toute seule (attente 0,5 s doublee jusqu'a 8 s) et envoie un ping regulier.
 * `path` = null desactive la connexion. Chaque message JSON (hors "pong") est transmis a `onMessage`.
 * Retourne `connected` pour que l'appelant puisse s'appuyer sur un sondage HTTP tant que la socket est coupee.
 */
export default function useSocket(path, onMessage) {
    const [connected, setConnected] = useState(false)
    const handler = useRef(onMessage)
    handler.current = onMessage

    useEffect(() => {
        const token = getToken()
        if (!path || !token) { setConnected(false); return }
        let ws, timer, beat, retry = 0, alive = true

        const open = () => {
            ws = new WebSocket(wsUrl(path), ["gtn.v1", token])      // le jeton voyage dans le sous-protocole, pas dans l'URL
            ws.onopen = () => {
                retry = 0
                setConnected(true)
                beat = setInterval(() => { if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: "ping" })) }, HEARTBEAT_MS)
            }
            ws.onmessage = (e) => {
                try {
                    const msg = JSON.parse(e.data)
                    if (msg.type !== "pong") handler.current?.(msg)
                } catch { /* message illisible: ignore */ }
            }
            ws.onclose = (e) => {
                clearInterval(beat)
                setConnected(false)
                if (e.code === 4401) window.dispatchEvent(new Event("gtn:auth-lost"))
                if (!alive || NO_RETRY.includes(e.code)) return
                timer = setTimeout(open, Math.min(8000, 500 * 2 ** retry++))
            }
            ws.onerror = () => ws.close()
        }

        open()
        return () => { alive = false; clearTimeout(timer); clearInterval(beat); ws?.close() }
    }, [path])

    return { connected }
}
