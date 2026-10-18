import { useEffect, useState } from "react"

// true tant que la media query correspond (se met a jour si la fenetre change)
export default function useMediaQuery(query) {
    const [matches, setMatches] = useState(() => window.matchMedia(query).matches)

    useEffect(() => {
        const mq = window.matchMedia(query)
        const onChange = () => setMatches(mq.matches)
        onChange()
        mq.addEventListener("change", onChange)
        return () => mq.removeEventListener("change", onChange)
    }, [query])

    return matches
}
