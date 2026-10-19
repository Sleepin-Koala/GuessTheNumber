import { useEffect, useState } from "react"
import { createAccount, restoreWithToken } from "../api/account"

// Affiche une alerte quand le serveur ne reconnait plus le jeton de ce navigateur (base reinitialisee, compte supprime...).
// On ne cree jamais un nouveau compte en silence: ce serait perdre la progression sans prevenir.
export default function SessionBanner() {
    const [lost, setLost] = useState(false)
    const [code, setCode] = useState("")
    const [error, setError] = useState("")
    const [busy, setBusy] = useState(false)

    useEffect(() => {
        const on = () => setLost(true)
        window.addEventListener("gtn:auth-lost", on)
        return () => window.removeEventListener("gtn:auth-lost", on)
    }, [])

    if (!lost) return null

    async function restore(e) {
        e.preventDefault(); setBusy(true); setError("")
        try { await restoreWithToken(code); window.location.reload() }
        catch { setError("Code invalide.") } finally { setBusy(false) }
    }
    async function fresh() {
        setBusy(true)
        try { localStorage.removeItem("token"); await createAccount(); window.location.reload() }
        catch (e) { setError(e.message) } finally { setBusy(false) }
    }

    return (
        <div role="alertdialog" aria-labelledby="session-lost" className="fixed inset-0 z-[200] grid place-items-center bg-black/80 p-4">
            <div className="w-full max-w-md rounded-3xl bg-linear-to-br from-indigo-800 to-purple-900 border-4 border-yellow-400 p-6 text-white flex flex-col gap-3">
                <h2 id="session-lost" className="text-3xl">Compte non reconnu</h2>
                <p className="font-bold text-white/85">Le serveur ne reconnaît plus ton compte. Si tu as un code de récupération, colle-le ici ; sinon tu peux repartir avec un nouveau compte.</p>
                <form onSubmit={restore} className="flex flex-col gap-2">
                    <input type="password" autoComplete="off" value={code} onChange={(e) => setCode(e.target.value)} aria-label="Code de récupération" placeholder="Code de récupération"
                        className="min-h-11 px-3 rounded-xl bg-white/15 border-2 border-white/30 focus:outline-none focus:border-yellow-400" />
                    <button type="submit" disabled={busy || !code.trim()} className="min-h-11 rounded-xl bg-yellow-400 text-black font-bold disabled:opacity-40">Restaurer mon compte</button>
                </form>
                <button type="button" onClick={fresh} disabled={busy} className="min-h-11 rounded-xl bg-white/15 font-bold">Créer un nouveau compte</button>
                {error && <p role="alert" className="text-red-200 font-bold">{error}</p>}
            </div>
        </div>
    )
}
