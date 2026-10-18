import { Component, lazy, Suspense, useMemo } from "react"
import useMediaQuery from "../hooks/useMediaQuery"

// three.js est charge uniquement quand une partie commence (hors du chemin critique de l'accueil)
const OrbScene = lazy(() => import("./OrbScene"))

function webglAvailable() {
    try {
        const c = document.createElement("canvas")
        return !!(c.getContext("webgl2") || c.getContext("webgl"))
    } catch { return false }
}

class Boundary extends Component {
    state = { failed: false }
    static getDerivedStateFromError() { return { failed: true } }
    render() { return this.state.failed ? this.props.fallback : this.props.children }
}

/**
 * Bonbon 3D mystere. `heat` va de 0 (loin) a 1 (tres proche), null = pas encore de proposition.
 * `fallback` est affiche si WebGL est absent, pendant le chargement ou si le chargement echoue.
 */
export default function MysteryOrb({ heat, hint, shaking, fallback }) {
    const hasRoom = useMediaQuery("(min-height: 701px)")
    const reduced = useMediaQuery("(prefers-reduced-motion: reduce)")
    const ok = useMemo(webglAvailable, [])

    if (!hasRoom) return null   // ecrans courts (paysage): on libere la place pour le champ de saisie
    if (!ok) return fallback

    return (
        <div className="relative w-36 h-36 sm:w-52 sm:h-52 shrink-0" role="img"
            aria-label="Bonbon mystère : sa couleur indique si tu te rapproches du nombre">
            <Boundary fallback={fallback}>
                <Suspense fallback={fallback}>
                    <OrbScene heat={heat} hint={hint} shaking={shaking} reduced={reduced} />
                </Suspense>
            </Boundary>
        </div>
    )
}
