import { useEffect, useState } from "react"
import { startAccount } from "../api/account"

// Les ecrans de jeu lisent l'id et le jeton du joueur au demarrage: on attend que le compte soit pret (en pratique
// c'est deja fait quand le code de l'ecran, charge a la demande, arrive). Pas d'attente pour l'accueil.
export default function AccountGate({ children }) {
    const [ready, setReady] = useState(false)
    useEffect(() => { startAccount().finally(() => setReady(true)) }, [])
    return ready ? children : <div className="min-h-dvh bg-[#150b30]" aria-busy="true" />
}
