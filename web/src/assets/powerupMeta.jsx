import { FaDice, FaSearch, FaHeart, FaRobot, FaHashtag, FaAward, FaHourglassHalf, FaFire } from "react-icons/fa"

// ids = ceux de la boutique / du backend (backend/routes/powerups.py)
export const ITEM = { PARITY: 1, SCAN: 2, LIFE: 3, ADVISOR: 4, PRIME: 5, PERFECT: 6, SLOW: 7, MULTIPLIER: 8 }

export const POWERUPS = {
    1: { name: "Nombre Pair", icon: <FaDice /> },
    2: { name: "Scan", icon: <FaSearch /> },
    3: { name: "Vie bonus", icon: <FaHeart /> },
    4: { name: "Conseiller IA", icon: <FaRobot /> },
    5: { name: "Premier", icon: <FaHashtag /> },
    6: { name: "Parfait", icon: <FaAward /> },
    7: { name: "Ralenti", icon: <FaHourglassHalf /> },
    8: { name: "Multiplicateur x2", icon: <FaFire /> },
}

// Phrase affichee apres l'utilisation d'un power-up (resultat renvoye par POST /game/powerup)
export function describeEffect(r) {
    switch (r.kind) {
        case "parity": return `Le nombre est ${r.value}`
        case "prime": return r.value ? "Le nombre est premier" : "Le nombre n'est pas premier"
        case "perfect": return r.value ? "Le nombre est parfait" : "Le nombre n'est pas parfait"
        case "range": return `Il est entre ${r.lo} et ${r.hi}`
        case "suggest": return `Conseil : essaie ${r.number} (entre ${r.lo} et ${r.hi})`
        case "attempts": return `+${r.extra} essais`
        case "time": return `+${r.extra} secondes`
        case "multiplier": return "Pièces x2 si tu gagnes"
        default: return "Power-up utilisé"
    }
}
