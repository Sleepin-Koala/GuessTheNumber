import { useEffect, useRef, useState } from "react"

// Fait defiler un nombre de sa valeur precedente vers la nouvelle (compteur de pieces / XP)
export default function useCountUp(value, duration = 600) {
    const [shown, setShown] = useState(value)
    const from = useRef(value)

    useEffect(() => {
        if (typeof value !== "number" || typeof from.current !== "number") { setShown(value); from.current = value; return }
        if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) { setShown(value); from.current = value; return }
        const start = performance.now(), a = from.current, b = value
        let raf
        const tick = (now) => {
            const p = Math.min(1, (now - start) / duration)
            const eased = 1 - Math.pow(1 - p, 3)
            setShown(Math.round(a + (b - a) * eased))
            if (p < 1) raf = requestAnimationFrame(tick)
            else from.current = b
        }
        raf = requestAnimationFrame(tick)
        return () => { cancelAnimationFrame(raf); from.current = b }
    }, [value, duration])

    return shown
}
