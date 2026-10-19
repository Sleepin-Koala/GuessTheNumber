import { useEffect, useState } from "react"
import { FaCoins, FaPlay } from "react-icons/fa"
import api from "../../api/index"
import { CartoonButton } from "../../components/assets"
import useSocket from "../../hooks/useSocket"

const BETS = [0, 50, 100, 250, 500]
const RANGES = [10, 50, 100, 500]

export default function Lobby({ player, onJoined, onHosted, onBack, notice }) {
    const [rooms, setRooms] = useState(null)
    const [error, setError] = useState("")
    const [name, setName] = useState("")
    const [bet, setBet] = useState(50)
    const [range, setRange] = useState(50)
    const [busy, setBusy] = useState(false)

    // la liste arrive en direct par WebSocket; le sondage HTTP ne sert que de filet de securite
    // (toutes les 15 s, ou toutes les 3 s tant que la socket est coupee)
    const { connected } = useSocket("/game/duel/ws-lobby", (msg) => { if (msg.type === "lobby") { setRooms(msg.rooms); setError("") } })

    useEffect(() => {
        let alive = true
        const load = async () => {
            try {
                const list = await api.get("/game/duel/rooms")
                if (alive) { setRooms(list); setError("") }
            } catch (e) {
                if (alive) setError(e.message)
            }
        }
        if (!connected) load()
        const id = setInterval(() => { if (!document.hidden) load() }, connected ? 15000 : 3000)
        return () => { alive = false; clearInterval(id) }
    }, [connected])

    async function host(e) {
        e.preventDefault()
        setBusy(true); setError("")
        try {
            const room = await api.post("/game/duel/host", {
                host_id: player.id, name: name.trim() || `Salle de ${player.name}`, amount: bet, max_range: range,
            })
            onHosted(room)
        } catch (err) { setError(err.message) } finally { setBusy(false) }
    }

    async function join(room) {
        setBusy(true); setError("")
        try {
            onJoined(await api.post("/game/duel/join", { player_id: player.id, room_id: room.room_id }))
        } catch (err) { setError(err.message) } finally { setBusy(false) }
    }

    const coins = player.coins ?? 0
    const open = (rooms ?? []).filter((r) => r.host_id !== player.id)

    return (
        <div className="mx-auto w-full max-w-5xl p-3 sm:p-6 grid gap-5 lg:grid-cols-2">
            <section className="candy-gloss candy-lip relative rounded-3xl bg-linear-to-b from-[#4b2d99] to-[#2a1560] border-2 border-white/25 p-5">
                <h2 className="text-3xl text-white">Créer une salle</h2>
                <form onSubmit={host} className="mt-4 flex flex-col gap-4">
                    <label className="flex flex-col gap-1 text-white font-bold">Nom de la salle
                        <input value={name} onChange={(e) => setName(e.target.value)} maxLength={30} placeholder={`Salle de ${player.name ?? "..."}`}
                            className="min-h-11 px-3 rounded-xl bg-white/15 border-2 border-white/30 text-white text-lg focus:outline-none focus:border-yellow-400" />
                    </label>

                    <fieldset>
                        <legend className="text-white font-bold mb-1">Mise (pièces)</legend>
                        <div className="flex flex-wrap gap-2">
                            {BETS.map((b) => (
                                <button key={b} type="button" disabled={b > coins} aria-pressed={bet === b} onClick={() => setBet(b)}
                                    className={`min-h-11 min-w-14 px-3 rounded-full font-game text-lg transition ${bet === b ? "bg-yellow-400 text-black" : "bg-white/15 text-white"} disabled:opacity-30`}>{b}</button>
                            ))}
                        </div>
                    </fieldset>

                    <fieldset>
                        <legend className="text-white font-bold mb-1">Le nombre est entre 1 et…</legend>
                        <div className="flex flex-wrap gap-2">
                            {RANGES.map((r) => (
                                <button key={r} type="button" aria-pressed={range === r} onClick={() => setRange(r)}
                                    className={`min-h-11 min-w-14 px-3 rounded-full font-game text-lg transition ${range === r ? "bg-yellow-400 text-black" : "bg-white/15 text-white"}`}>{r}</button>
                            ))}
                        </div>
                    </fieldset>

                    <CartoonButton className="min-h-11 px-6 py-3 text-xl" onClick={undefined}>
                        <span className="flex items-center justify-center gap-2"><FaPlay /> {busy ? "Création…" : "Créer la salle"}</span>
                    </CartoonButton>
                </form>
            </section>

            <section className="candy-gloss candy-lip relative rounded-3xl bg-linear-to-b from-[#1f4e8c] to-[#14305a] border-2 border-white/25 p-5">
                <div className="flex items-center justify-between gap-2">
                    <h2 className="text-3xl text-white">Salles ouvertes</h2>
                    <span className={`flex items-center gap-1.5 text-sm font-bold ${connected ? "text-emerald-300" : "text-amber-300"}`} role="status">
                        <span className={`w-2.5 h-2.5 rounded-full ${connected ? "bg-emerald-400" : "bg-amber-400 animate-pulse"}`} aria-hidden="true" />
                        {connected ? "En direct" : "Reconnexion…"}
                    </span>
                </div>

                {rooms === null && <p className="mt-4 text-white/70 font-bold">Chargement…</p>}
                {rooms !== null && open.length === 0 && (
                    <p className="mt-4 text-white/80 font-bold">Aucune salle pour l'instant. Crée la tienne et attends un adversaire.</p>
                )}

                <ul className="mt-4 flex flex-col gap-3">
                    {open.map((r) => (
                        <li key={r.room_id} className="flex items-center justify-between gap-3 rounded-2xl bg-black/25 p-3">
                            <div className="min-w-0">
                                <div className="text-xl text-white truncate font-game">{r.room_name}</div>
                                <div className="text-sm text-white/70 truncate">{r.host_name ?? "Joueur"} · 1 à {r.max_range}</div>
                            </div>
                            <div className="flex items-center gap-3 shrink-0">
                                <span className="flex items-center gap-1 text-yellow-200 font-bold"><FaCoins aria-hidden="true" />{r.bet_amount}</span>
                                <button onClick={() => join(r)} disabled={busy || r.bet_amount > coins}
                                    className="min-h-11 px-4 rounded-full bg-linear-to-b from-[#ffe066] to-[#ff9f1c] text-[#3b1d00] font-game text-lg shadow-[0_4px_0_#b45309] active:translate-y-0.5 disabled:opacity-40">
                                    {r.bet_amount > coins ? "Trop cher" : "Rejoindre"}
                                </button>
                            </div>
                        </li>
                    ))}
                </ul>
            </section>

            {notice && <p role="status" className="lg:col-span-2 rounded-2xl bg-amber-300 text-black font-bold p-3 text-center">{notice}</p>}
            {error && <p role="alert" className="lg:col-span-2 rounded-2xl bg-red-500/85 text-white font-bold p-3 text-center">{error}</p>}

            <div className="lg:col-span-2 flex justify-center">
                <CartoonButton className="min-h-11 px-6 py-2 text-lg" onClick={onBack}>Retour</CartoonButton>
            </div>
        </div>
    )
}
