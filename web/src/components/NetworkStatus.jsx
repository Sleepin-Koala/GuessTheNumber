import { useEffect, useState } from "react"

// Bandeau "hors ligne" + invitation a recharger quand une nouvelle version (service worker) est prete.
export default function NetworkStatus() {
    const [online, setOnline] = useState(() => navigator.onLine)
    const [registration, setRegistration] = useState(null)

    useEffect(() => {
        const up = () => setOnline(true)
        const down = () => setOnline(false)
        const onUpdate = (e) => setRegistration(e.detail)
        window.addEventListener("online", up)
        window.addEventListener("offline", down)
        window.addEventListener("sw-update", onUpdate)
        return () => {
            window.removeEventListener("online", up)
            window.removeEventListener("offline", down)
            window.removeEventListener("sw-update", onUpdate)
        }
    }, [])

    function applyUpdate() {
        navigator.serviceWorker.addEventListener("controllerchange", () => window.location.reload(), { once: true })
        registration?.waiting?.postMessage("SKIP_WAITING")
    }

    if (online && !registration) return null

    return (
        <div role="status" aria-live="polite"
            className="fixed inset-x-0 bottom-0 z-[100] flex flex-wrap items-center justify-center gap-3 px-4 py-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] text-sm font-bold text-black bg-cartoon-yellow shadow-simple">
            {!online
                ? <span>Hors ligne : les parties et la boutique ont besoin du serveur.</span>
                : <span>Une nouvelle version est disponible.</span>}
            {online && registration &&
                <button onClick={applyUpdate} className="min-h-11 px-4 rounded-xl bg-black text-white">Mettre à jour</button>}
        </div>
    )
}
