import { useCallback, useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
import api from "../../api/index"
import BG from "../../components/Background"
import Bar from "../../components/PlayerProps"
import { CartoonButton } from "../../components/assets"
import Lobby from "./Lobby"
import { RoomHeader, Waiting, Hide, WaitHide, Guess, Watch, Result } from "./RoomViews"

const STORE = "duel_room"
const POLL_MS = 1500
const ACTIVE = (s) => s && s !== "finished" && s !== "cancelled"

// Duel: deux joueurs, chacun cache un nombre puis cherche celui de l'autre; le moins d'essais gagne la mise.
// L'etat de la salle vient du serveur (sondage toutes les 1,5 s): rien n'est decide cote client.
export default function Duel() {
    const navigate = useNavigate()
    const [player, setPlayer] = useState(null)
    const [room, setRoom] = useState(null)
    const [error, setError] = useState("")
    const [busy, setBusy] = useState(false)
    const [mySecret, setMySecret] = useState(null)
    const [coinsBefore, setCoinsBefore] = useState(null)
    const [coinsNow, setCoinsNow] = useState(null)
    const hold = useRef(false)

    const loadPlayer = useCallback(async () => {
        const id = localStorage.getItem("id")
        if (!id) return null
        const p = await api.get(`/user/${id}`)
        setPlayer(p)
        return p
    }, [])

    const remember = (r, extra = {}) => {
        const prev = JSON.parse(localStorage.getItem(STORE) ?? "{}")
        localStorage.setItem(STORE, JSON.stringify({ ...prev, room_id: r.room_id, ...extra }))
    }
    const forget = () => localStorage.removeItem(STORE)

    // chargement + reprise d'une partie en cours apres un rechargement de page
    useEffect(() => {
        (async () => {
            try {
                const p = await loadPlayer()
                const saved = JSON.parse(localStorage.getItem(STORE) ?? "null")
                if (p && saved?.room_id) {
                    const r = await api.post("/game/duel/status", { room_id: saved.room_id })
                    if (ACTIVE(r.status) && (r.host_id === p.id || r.guest_id === p.id)) {
                        setRoom(r); setCoinsBefore(saved.coinsBefore ?? p.coins); setMySecret(saved.secret ?? null)
                    } else forget()
                }
            } catch (e) { setError(e.message); forget() }
        })()
    }, [loadPlayer])

    // sondage de l'etat de la salle tant que la partie n'est pas terminee
    const roomId = room?.room_id, status = room?.status
    useEffect(() => {
        if (!roomId || !ACTIVE(status)) return
        const tick = async () => {
            if (document.hidden || hold.current) return
            try {
                const next = await api.post("/game/duel/status", { room_id: roomId })
                setRoom((prev) => (JSON.stringify(prev) === JSON.stringify(next) ? prev : next))
                setError("")
            } catch (e) {
                setError(`Connexion perdue : ${e.message}. Nouvel essai en cours…`)
            }
        }
        const id = setInterval(tick, POLL_MS)
        return () => clearInterval(id)
    }, [roomId, status])

    // fin de partie / salle annulee
    useEffect(() => {
        if (status === "finished") { forget(); loadPlayer().then((p) => setCoinsNow(p?.coins ?? null)).catch(() => {}) }
        if (status === "cancelled") { forget(); setRoom(null) }
    }, [status, loadPlayer])

    const enter = (r) => { setRoom(r); setCoinsBefore(player.coins); setMySecret(null); setCoinsNow(null); remember(r, { coinsBefore: player.coins, secret: null }) }

    async function cancel() {
        setBusy(true)
        try { await api.post(`/game/duel/rooms/${room.room_id}/leave`, { player_id: player.id }); forget(); setRoom(null) }
        catch (e) { setError(e.message) } finally { setBusy(false) }
    }

    async function hide(n) {
        const next = await api.post(`/game/duel/rooms/${room.room_id}/hide`, { player_id: player.id, number: n })
        setMySecret(n); remember(next, { secret: n }); setRoom(next)
    }

    function done() { forget(); setRoom(null); setCoinsNow(null); loadPlayer().catch(() => {}) }

    const me = player?.id
    const isHost = room?.host_id === me
    const opponent = room ? (isHost ? room.guest_name : room.host_name) : null
    const round = status?.startsWith("round1") ? 1 : status?.startsWith("round2") ? 2 : null
    const attempts = round === 1 ? room?.round1_attempts_used : room?.round2_attempts_used

    let view = null
    if (room && me) {
        if (status === "waiting") view = isHost ? <Waiting room={room} onCancel={cancel} busy={busy} /> : null
        else if (status?.endsWith("_hide")) view = room.current_hider_id === me ? <Hide room={room} opponent={opponent} onHide={hide} /> : <WaitHide opponent={opponent} />
        else if (status?.endsWith("_guess")) view = room.current_guesser_id === me
            ? <Guess key={status} room={room} me={me} opponent={opponent} round={round} attempts={attempts ?? 0} onRoom={setRoom} onHold={(b) => { hold.current = b }} />
            : <Watch room={room} opponent={opponent} attempts={attempts ?? 0} mySecret={mySecret} />
    }

    return (
        <>
            <BG />
            <div className="flex flex-col h-dvh w-full">
                <Bar coins={player?.coins} gems={player?.gems} xp={player?.xp} name={player?.name} level={player?.level} />

                {error && <p role="alert" className="mx-auto mb-2 max-w-3xl rounded-2xl bg-red-500/85 text-white font-bold px-4 py-2 text-center">{error}</p>}

                {!room && (
                    <div className="flex-1 min-h-0 overflow-y-auto">
                        {player
                            ? <Lobby player={player} onJoined={enter} onHosted={enter} onBack={() => navigate("/")} />
                            : <p className="text-center text-white/80 font-bold p-8">{error ? "" : "Chargement…"}</p>}
                    </div>
                )}

                {room && me && (
                    <>
                        <RoomHeader room={room} opponent={opponent} round={round} />
                        <main className="flex-1 min-h-0 overflow-y-auto flex flex-col justify-center py-4">{view}</main>
                        {status === "finished" && <Result room={room} me={me} opponent={opponent} coinsBefore={coinsBefore} coinsNow={coinsNow} onDone={done} />}
                    </>
                )}
            </div>
        </>
    )
}
