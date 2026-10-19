import { useEffect, useState } from "react"
import { FaCoins, FaTrophy, FaHeartBroken } from "react-icons/fa"
import api from "../../api/index"
import GameplayPanel from "../../components/GameplayPanel"
import { CartoonButton } from "../../components/assets"
import useCountUp from "../../hooks/useCountUp"
import useCountdown, { mmss } from "../../hooks/useCountdown"

// Carte centrale commune aux ecrans d'attente
function Card({ children }) {
    return (
        <div className="candy-gloss candy-lip relative mx-auto w-[92%] max-w-lg rounded-3xl bg-linear-to-b from-[#4b2d99] to-[#2a1560] border-2 border-white/25 p-6 text-center flex flex-col items-center gap-4">
            {children}
        </div>
    )
}

export function RoomHeader({ room, opponent, round, live, opponentOnline }) {
    return (
        <div className="mx-auto w-full max-w-3xl px-3 pt-2 flex flex-wrap items-center justify-center gap-2 text-sm font-bold">
            <span className="px-3 py-1 rounded-full bg-black/40 text-white">{room.room_name}</span>
            <span className="px-3 py-1 rounded-full bg-black/40 text-white flex items-center gap-1.5">
                {opponent && <span className={`w-2.5 h-2.5 rounded-full ${opponentOnline ? "bg-emerald-400" : "bg-slate-500"}`} role="img" aria-label={opponentOnline ? "adversaire connecté" : "adversaire hors ligne"} />}
                contre {opponent ?? "…"}
            </span>
            <span className="px-3 py-1 rounded-full bg-black/40 text-yellow-200 flex items-center gap-1"><FaCoins aria-hidden="true" />{room.bet_amount}</span>
            {round && <span className="px-3 py-1 rounded-full bg-yellow-400 text-black">Manche {round}/2</span>}
            <span className={`px-3 py-1 rounded-full bg-black/40 flex items-center gap-1.5 ${live ? "text-emerald-300" : "text-amber-300"}`} role="status">
                <span className={`w-2.5 h-2.5 rounded-full ${live ? "bg-emerald-400" : "bg-amber-400 animate-pulse"}`} aria-hidden="true" />
                {live ? "En direct" : "Reconnexion…"}
            </span>
        </div>
    )
}

// Qui doit jouer, et combien de temps il lui reste avant de perdre par forfait
export function TurnTimer({ room, me, opponent }) {
    const left = useCountdown(room.status === "waiting" ? null : room.turn_deadline, room.server_time)
    if (left === null) return null
    const actor = room.status.endsWith("_hide") ? room.current_hider_id : room.current_guesser_id
    const mine = actor === me
    return (
        <span className={`px-3 py-1 rounded-full font-bold ${left <= 10 ? "bg-red-500 text-white animate-pulse" : left <= 20 ? "bg-amber-300 text-black" : "bg-black/40 text-white"}`} role="timer" aria-label={`${left} secondes restantes`}>
            {mine ? "Ton tour" : `Tour de ${opponent ?? "l'adversaire"}`} : {mmss(left)}
        </span>
    )
}

// L'adversaire a perdu la connexion: il a quelques secondes pour revenir, sinon il perd
export function OpponentGone({ grace, opponent }) {
    const left = useCountdown(grace?.deadline ?? null, grace?.server_time)
    if (!grace) return null
    return (
        <p role="alert" className="mx-auto mt-2 max-w-xl rounded-2xl bg-amber-300 text-black font-bold px-4 py-2 text-center">
            {opponent ?? "Ton adversaire"} s'est déconnecté. Victoire par forfait dans {left ?? 0} s s'il ne revient pas.
        </p>
    )
}

// Abandon volontaire, avec confirmation (la mise est perdue)
export function ForfeitButton({ onForfeit, bet }) {
    const [asking, setAsking] = useState(false)
    const [busy, setBusy] = useState(false)
    if (!asking) {
        return <button type="button" onClick={() => setAsking(true)} className="min-h-11 px-5 rounded-full bg-white/10 text-white/80 font-bold hover:bg-white/20">Abandonner</button>
    }
    return (
        <div className="flex flex-wrap items-center justify-center gap-2 text-white font-bold" role="alertdialog" aria-label="Confirmer l'abandon">
            <span>Abandonner et perdre {bet} pièces ?</span>
            <button type="button" disabled={busy} onClick={async () => { setBusy(true); try { await onForfeit() } finally { setBusy(false); setAsking(false) } }}
                className="min-h-11 px-4 rounded-full bg-red-500 text-white">Oui, abandonner</button>
            <button type="button" onClick={() => setAsking(false)} className="min-h-11 px-4 rounded-full bg-white/20">Non</button>
        </div>
    )
}

export function Waiting({ room, onCancel, busy }) {
    return (
        <Card>
            <h2 className="text-3xl text-white">En attente d'un adversaire</h2>
            <div className="flex gap-2" aria-hidden="true">
                {[0, 1, 2].map((i) => <span key={i} className="w-4 h-4 rounded-full bg-yellow-300 animate-bounce" style={{ animationDelay: `${i * 160}ms` }} />)}
            </div>
            <p className="text-white/80 font-bold">« {room.room_name} » est visible dans le lobby. Mise : {room.bet_amount} pièces, nombre entre 1 et {room.max_range}.</p>
            <CartoonButton className="min-h-11 px-6 py-2 text-lg" onClick={onCancel}>{busy ? "Annulation…" : "Annuler la salle"}</CartoonButton>
        </Card>
    )
}

export function Hide({ room, opponent, onHide }) {
    const [value, setValue] = useState("")
    const [busy, setBusy] = useState(false)
    const [error, setError] = useState("")
    const n = parseInt(value, 10)
    const valid = Number.isInteger(n) && n >= 1 && n <= room.max_range

    async function submit(e) {
        e.preventDefault()
        if (!valid) return
        setBusy(true); setError("")
        try { await onHide(n) } catch (err) { setError(err.message) } finally { setBusy(false) }
    }

    return (
        <Card>
            <h2 className="text-3xl text-white">Cache ton nombre</h2>
            <p className="text-white/80 font-bold">{opponent ?? "Ton adversaire"} devra le trouver entre 1 et {room.max_range}. Moins il lui faut d'essais, plus il a de chances de gagner.</p>
            <form onSubmit={submit} className="flex flex-col items-center gap-3 w-full">
                <input type="number" inputMode="numeric" min={1} max={room.max_range} value={value} onChange={(e) => setValue(e.target.value)} autoFocus
                    aria-label={`Ton nombre secret entre 1 et ${room.max_range}`} placeholder={`1 à ${room.max_range}`}
                    className="w-full max-w-xs min-h-14 px-4 rounded-xl text-center text-3xl text-white font-black bg-white/15 border-2 border-white/30 focus:outline-none focus:border-yellow-400" />
                {value !== "" && !valid && <p role="alert" className="text-red-200 font-bold">Choisis un nombre entre 1 et {room.max_range}.</p>}
                {error && <p role="alert" className="text-red-200 font-bold">{error}</p>}
                <CartoonButton className="min-h-11 px-6 py-3 text-xl" onClick={undefined}>{busy ? "Envoi…" : "Cacher mon nombre"}</CartoonButton>
            </form>
        </Card>
    )
}

export function WaitHide({ opponent }) {
    return (
        <Card>
            <h2 className="text-3xl text-white">{opponent ?? "Ton adversaire"} choisit son nombre…</h2>
            <div className="flex gap-2" aria-hidden="true">
                {[0, 1, 2].map((i) => <span key={i} className="w-4 h-4 rounded-full bg-yellow-300 animate-bounce" style={{ animationDelay: `${i * 160}ms` }} />)}
            </div>
        </Card>
    )
}

// Je devine le nombre de l'adversaire: meme panneau (et meme bonbon 3D) que les modes solo
export function Guess({ room, me, opponent, round, attempts, onRoom, onHold }) {
    const [localNumber, setLocalNumber] = useState("")
    const [hint, setHint] = useState("")
    const [distance, setDistance] = useState(0)
    const [numbers, setNumbers] = useState([])
    const [shake, setShake] = useState(false)
    const [found, setFound] = useState(false)
    const [error, setError] = useState("")

    useEffect(() => { const t = setTimeout(() => setShake(false), 350); return () => clearTimeout(t) }, [shake])
    // chaque manche repart d'un panneau vierge
    useEffect(() => { setLocalNumber(""); setHint(""); setNumbers([]); setDistance(0); setFound(false) }, [round])

    async function guess() {
        const n = parseInt(localNumber, 10)
        if (found || !Number.isInteger(n)) return
        try {
            const next = await api.post(`/game/duel/rooms/${room.room_id}/guess`, { player_id: me, number: n })
            setHint(next.last_feedback); setDistance(next.last_distance ?? 0); setLocalNumber("")
            if (next.last_feedback === "OK") {
                setFound(true)
                // on laisse le bonbon eclater avant de changer d'ecran (le sondage du serveur est suspendu)
                // l'etat suivant est mis en attente (les mises a jour en direct aussi) puis applique apres l'animation
                onHold(true)
                onRoom(next)
                setTimeout(() => onHold(false), 1700)
            } else {
                setNumbers((prev) => [...prev, [n, next.last_feedback]].slice(-6)); setShake(true)
                onRoom(next)
            }
            setError("")
        } catch (e) {
            setError(e.message)
        }
    }

    return (
        <div className="flex flex-1 min-h-0 overflow-y-auto">
            <GameplayPanel hint={hint} distance={distance} numbers={numbers} isShaking={shake} range={room.max_range}
                localNumber={localNumber} NumberSetter={setLocalNumber} onGuessr={guess} attempt={attempts}
                gameEnded={found} onGameEnded={() => {}} showPause={false}
                infos={[{ text: `Trouve le nombre de ${opponent ?? "ton adversaire"}` }, ...(error ? [{ text: error, error: true }] : [])]} />
        </div>
    )
}

// Je suis celui qui a cache son nombre: je regarde l'autre chercher
export function Watch({ room, opponent, attempts, mySecret }) {
    const fb = room.last_feedback
    return (
        <Card>
            <h2 className="text-3xl text-white">{opponent ?? "Ton adversaire"} cherche ton nombre</h2>
            <div className="grid place-items-center w-28 h-28 rounded-full bg-yellow-300 ring-4 ring-white/50 shadow-[inset_0_-6px_0_rgba(0,0,0,.2)]" aria-label={`${attempts} essais`}>
                <span className="font-game text-6xl text-black tabular-nums">{attempts ?? 0}</span>
            </div>
            <p className="text-white/80 font-bold">essai{(attempts ?? 0) > 1 ? "s" : ""} jusqu'ici</p>
            {fb && fb !== "OK" && <p className="px-3 py-1 rounded-full bg-white/90 text-indigo-950 font-bold">Dernière proposition : {fb === "MOINS" ? "trop petite" : "trop grande"} (écart {room.last_distance})</p>}
            {mySecret != null && <p className="text-white/60 text-sm">Ton nombre secret : {mySecret}</p>}
        </Card>
    )
}

function reasonText(reason, won, opponent) {
    const them = opponent ?? "Ton adversaire"
    switch (reason) {
        case "forfeit": return won ? `${them} a abandonné.` : "Tu as abandonné."
        case "disconnect": return won ? `${them} s'est déconnecté trop longtemps.` : "Tu as été déconnecté trop longtemps."
        case "timeout": return won ? `${them} n'a pas joué à temps.` : "Tu n'as pas joué à temps."
        default: return won ? `Tu as battu ${them}.` : `${them} a gagné.`
    }
}

export function Result({ room, me, opponent, coinsBefore, coinsNow, onDone }) {
    const won = room.winner_id === me
    const isHost = room.host_id === me
    const mine = isHost ? room.round2_attempts_used : room.round1_attempts_used
    const theirs = isHost ? room.round1_attempts_used : room.round2_attempts_used
    const delta = coinsNow != null && coinsBefore != null ? coinsNow - coinsBefore : null
    const shown = useCountUp(delta ?? 0, 900)

    return (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/75 p-4">
            <div className="candy-gloss candy-lip relative w-full max-w-sm rounded-3xl bg-linear-to-b from-[#4b2d99] to-[#2a1560] border-2 border-white/30 p-6 text-center flex flex-col items-center gap-3" role="dialog" aria-modal="true" aria-labelledby="duel-result">
                <div className={`text-6xl ${won ? "text-amber-300" : "text-slate-300"}`}>{won ? <FaTrophy /> : <FaHeartBroken />}</div>
                <h2 id="duel-result" className="text-4xl text-white">{won ? "Victoire !" : "Défaite"}</h2>
                <p className="text-white/80 font-bold">
                    {reasonText(room.end_reason, won, opponent)}
                    {(room.end_reason ?? "solved") === "solved" && mine === theirs && " Égalité d'essais : l'hôte l'emporte."}
                </p>
                {(room.end_reason ?? "solved") === "solved" && (
                    <div className="grid grid-cols-2 gap-3 w-full text-white">
                        <div className="rounded-2xl bg-black/30 p-2"><div className="text-sm text-white/70">Tes essais</div><div className="font-game text-3xl">{mine}</div></div>
                        <div className="rounded-2xl bg-black/30 p-2"><div className="text-sm text-white/70">Ses essais</div><div className="font-game text-3xl">{theirs}</div></div>
                    </div>
                )}
                {delta !== null && (
                    <div className={`flex items-center gap-2 font-game text-3xl ${shown >= 0 ? "text-yellow-300" : "text-red-300"}`}><FaCoins aria-hidden="true" />{shown > 0 ? "+" : ""}{shown}</div>
                )}
                <CartoonButton className="min-h-11 px-6 py-3 text-xl" onClick={onDone}>Retour au lobby</CartoonButton>
            </div>
        </div>
    )
}
