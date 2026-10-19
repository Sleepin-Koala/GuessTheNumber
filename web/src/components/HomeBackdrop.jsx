import { lazy, Suspense, useEffect, useMemo, useState } from "react"
import Bg from "./Background"
import { Boundary, webglAvailable, gpuAccelerated } from "./webgl"
import useMediaQuery from "../hooks/useMediaQuery"

// La scene 3D (three.js) est chargee apres le premier affichage; en attendant, ou sans WebGL,
// c'est le decor SVG d'origine qui reste visible.
const HomeScene = lazy(() => import("./HomeScene"))

export default function HomeBackdrop() {
    const ok = useMemo(() => webglAvailable() && gpuAccelerated(), [])
    const reduced = useMediaQuery("(prefers-reduced-motion: reduce)")
    const [ready, setReady] = useState(false)

    useEffect(() => {
        if (!ok) return
        const start = () => setReady(true)
        const id = ("requestIdleCallback" in window)
            ? window.requestIdleCallback(start, { timeout: 2500 })
            : window.setTimeout(start, 1500)
        return () => ("cancelIdleCallback" in window ? window.cancelIdleCallback(id) : window.clearTimeout(id))
    }, [ok])

    return (
        <>
            <Bg />
            {ok && ready && (
                <Boundary fallback={null}>
                    <Suspense fallback={null}>
                        <div aria-hidden="true" className="fixed inset-0 -z-[5] animate-[fade-in_1.2s_ease-out_both] bg-[radial-gradient(ellipse_at_50%_35%,#2d1566_0%,#150b30_70%)]">
                            <HomeScene reduced={reduced} />
                        </div>
                    </Suspense>
                </Boundary>
            )}
        </>
    )
}
