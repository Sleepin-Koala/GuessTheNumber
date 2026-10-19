import { useState } from "react"
import { FaCopy, FaKey } from "react-icons/fa"
import { getToken, restoreWithToken } from "../api/account"

// Le code de recuperation est le jeton secret du compte: le copier permet de retrouver sa progression sur un autre appareil.
export default function AccountRecovery() {
    const [copied, setCopied] = useState(false)
    const [shownCode, setShownCode] = useState(null)
    const [code, setCode] = useState("")
    const [busy, setBusy] = useState(false)
    const [error, setError] = useState("")

    async function copy() {
        try {
            await navigator.clipboard.writeText(getToken() ?? "")
            setCopied(true); setTimeout(() => setCopied(false), 2000)
        } catch {
            setShownCode(getToken())          // presse-papiers indisponible: on affiche le code pour le recopier
        }
    }

    async function restore(e) {
        e.preventDefault()
        if (!code.trim()) return
        setBusy(true); setError("")
        try {
            await restoreWithToken(code)
            window.location.reload()
        } catch {
            setError("Code invalide : ce compte est introuvable.")
        } finally { setBusy(false) }
    }

    return (
        <section className="mb-5 rounded-xl bg-black/25 p-3 text-white" aria-labelledby="account-title">
            <h3 id="account-title" className="flex items-center gap-2 font-bold"><FaKey aria-hidden="true" /> Ton compte</h3>
            <p className="text-sm text-white/75 mt-1">Ton code de récupération donne accès à ta progression. Garde-le secret et ne le partage jamais.</p>

            <button type="button" onClick={copy} className="mt-2 min-h-11 px-4 rounded-xl bg-white/20 font-bold flex items-center gap-2">
                <FaCopy aria-hidden="true" /> {copied ? "Copié !" : "Copier mon code de récupération"}
            </button>
            {shownCode && <p className="mt-2 break-all select-text rounded bg-black/40 p-2 text-xs" role="status">{shownCode}</p>}

            <form onSubmit={restore} className="mt-3 flex flex-col gap-2">
                <label htmlFor="recovery-code" className="text-sm font-bold">Restaurer un compte</label>
                <input id="recovery-code" type="password" autoComplete="off" value={code} onChange={(e) => setCode(e.target.value)} placeholder="Colle un code de récupération"
                    className="min-h-11 px-3 rounded-xl bg-white/15 border-2 border-white/30 text-white focus:outline-none focus:border-yellow-400" />
                {error && <p role="alert" className="text-red-200 font-bold text-sm">{error}</p>}
                <button type="submit" disabled={busy || !code.trim()} className="min-h-11 px-4 rounded-xl bg-yellow-400 text-black font-bold disabled:opacity-40">{busy ? "Vérification…" : "Restaurer"}</button>
                <p className="text-xs text-white/60">Le compte actuel de cet appareil sera remplacé : copie d'abord son code si tu veux pouvoir le retrouver.</p>
            </form>
        </section>
    )
}
