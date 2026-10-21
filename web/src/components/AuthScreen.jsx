import { useEffect, useRef, useState } from "react"
import { motion } from "framer-motion"
import { FaEye, FaEyeSlash } from "react-icons/fa"
import { authConfig, finishAuth, loginEmail, loginGoogle, playAsGuest, registerEmail, getToken } from "../api/account"

const GSI = "https://accounts.google.com/gsi/client"

function loadGoogle() {
    return new Promise((resolve, reject) => {
        if (window.google?.accounts?.id) return resolve(window.google)
        const el = document.createElement("script")
        el.src = GSI; el.async = true
        el.onload = () => resolve(window.google); el.onerror = reject
        document.head.appendChild(el)
    })
}

// Formulaire commun: ecran d'accueil (premiere visite) et fenetre "Sauvegarder ma progression" (reglages).
export default function AuthScreen({ linking = false, onClose }) {
    const [mode, setMode] = useState(linking ? "register" : "register")     // register | login
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [show, setShow] = useState(false)
    const [error, setError] = useState("")
    const [busy, setBusy] = useState(false)
    const [googleId, setGoogleId] = useState(null)
    const gbtn = useRef(null)

    const done = (player) => { finishAuth(player); onClose?.() }

    async function submit(e) {
        e.preventDefault(); setBusy(true); setError("")
        try { done(await (mode === "register" ? registerEmail : loginEmail)(email, password)) }
        catch (err) { setError(err.message) } finally { setBusy(false) }
    }

    useEffect(() => { authConfig().then((c) => setGoogleId(c.google_client_id)) }, [])
    useEffect(() => {
        if (!googleId || !gbtn.current) return
        let cancelled = false
        loadGoogle().then((google) => {
            if (cancelled) return
            google.accounts.id.initialize({
                client_id: googleId,
                callback: async ({ credential }) => {
                    setBusy(true); setError("")
                    try { done(await loginGoogle(credential)) } catch (err) { setError(err.message) } finally { setBusy(false) }
                },
            })
            google.accounts.id.renderButton(gbtn.current, { theme: "filled_black", size: "large", shape: "pill", text: "continue_with", locale: "fr", width: 300 })
        }).catch(() => setError("Google est inaccessible pour le moment. Utilise ton e-mail."))
        return () => { cancelled = true }
    }, [googleId])

    const input = "min-h-12 w-full rounded-2xl bg-black/35 px-4 text-lg font-bold text-white ring-2 ring-white/20 placeholder:text-white/40 focus:outline-none focus:ring-4 focus:ring-yellow-300"

    return (
        <motion.section role="dialog" aria-modal="true" aria-labelledby="auth-title" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="fixed inset-0 z-[300] overflow-y-auto bg-[radial-gradient(ellipse_at_50%_20%,#5b2a9e_0%,#2a1060_55%,#14062e_100%)] text-white">
            <div className="mx-auto flex min-h-full w-full max-w-sm flex-col justify-center gap-4 px-5 py-8">
                <h1 id="auth-title" className="font-game text-4xl leading-tight">{linking ? "Sauvegarde ta progression" : "Retrouve ta partie partout"}</h1>
                <p className="font-bold text-white/80">{linking ? "Lie un e-mail ou Google à ce compte : tes pièces et ton niveau te suivent sur tous tes appareils." : "Crée un compte pour garder tes pièces, ton niveau et tes duels, même si tu changes de téléphone."}</p>

                <div className="grid grid-cols-2 gap-1 rounded-2xl bg-black/30 p-1" role="tablist">
                    {[["register", "Créer un compte"], ["login", "Se connecter"]].map(([k, label]) => (
                        <button key={k} type="button" role="tab" aria-selected={mode === k} onClick={() => { setMode(k); setError("") }}
                            className={`min-h-11 rounded-xl font-game text-lg ${mode === k ? "bg-yellow-300 text-[#4a2200]" : "text-white/80"}`}>{label}</button>
                    ))}
                </div>

                <form onSubmit={submit} className="flex flex-col gap-3">
                    <input type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Adresse e-mail" aria-label="Adresse e-mail" className={input} />
                    <div className="relative">
                        <input type={show ? "text" : "password"} autoComplete={mode === "register" ? "new-password" : "current-password"} required minLength={mode === "register" ? 8 : 1}
                            value={password} onChange={(e) => setPassword(e.target.value)} placeholder={mode === "register" ? "Mot de passe (8 caractères min.)" : "Mot de passe"} aria-label="Mot de passe" className={`${input} pr-12`} />
                        <button type="button" onClick={() => setShow(!show)} aria-label={show ? "Masquer le mot de passe" : "Afficher le mot de passe"} className="absolute right-1 top-1/2 grid h-10 w-10 -translate-y-1/2 place-items-center text-white/70">
                            {show ? <FaEyeSlash aria-hidden="true" /> : <FaEye aria-hidden="true" />}
                        </button>
                    </div>
                    {error && <p role="alert" className="rounded-xl bg-rose-500/30 px-3 py-2 font-bold ring-1 ring-rose-200/40">{error}</p>}
                    <button type="submit" disabled={busy} className="min-h-14 rounded-2xl bg-linear-to-b from-[#7cf29a] to-[#27b35a] font-game text-2xl text-[#073b1a] shadow-[0_6px_0_rgba(0,0,0,.3)] active:translate-y-0.5 disabled:opacity-50">
                        {busy ? "Un instant…" : mode === "register" ? "Créer mon compte" : "Me connecter"}
                    </button>
                </form>

                {googleId && (<>
                    <div className="flex items-center gap-3 text-sm font-bold text-white/60"><span className="h-px flex-1 bg-white/20" />ou<span className="h-px flex-1 bg-white/20" /></div>
                    <div ref={gbtn} className="flex min-h-11 justify-center" />
                </>)}

                {linking
                    ? <button type="button" onClick={onClose} className="min-h-11 font-bold text-white/70 underline">Plus tard</button>
                    : <button type="button" onClick={async () => { setBusy(true); try { await playAsGuest(); onClose?.() } catch (err) { setError(err.message) } finally { setBusy(false) } }} disabled={busy} className="min-h-11 font-bold text-white/70 underline">Jouer sans compte pour l'instant</button>}
            </div>
        </motion.section>
    )
}

// Affiche l'ecran d'accueil tant que le joueur n'a ni compte ni jeton
export function AuthGate() {
    const [open, setOpen] = useState(false)
    useEffect(() => {
        const on = () => setOpen(true)
        window.addEventListener("gtn:need-auth", on)
        import("../api/account").then((m) => m.isAwaitingAuth() && setOpen(true))
        return () => window.removeEventListener("gtn:need-auth", on)
    }, [])
    return open && !getToken() ? <AuthScreen onClose={() => setOpen(false)} /> : null
}
