import { useEffect, useMemo, useState } from "react"

// Secondes restantes avant `deadline` (epoch serveur). `serverTime` = heure du serveur au moment de l'envoi:
// on en deduit le decalage d'horloge, donc le compte a rebours est juste meme si l'heure du telephone est fausse.
export default function useCountdown(deadline, serverTime) {
    const [, setTick] = useState(0)
    const offset = useMemo(() => (serverTime != null ? Date.now() / 1000 - serverTime : 0), [serverTime, deadline])

    useEffect(() => {
        if (deadline == null) return
        const id = setInterval(() => setTick((n) => n + 1), 1000)
        return () => clearInterval(id)
    }, [deadline])

    if (deadline == null) return null
    return Math.max(0, Math.round(deadline - (Date.now() / 1000 - offset)))
}

export const mmss = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`
