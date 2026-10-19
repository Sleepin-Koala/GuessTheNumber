import { useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
import { FaCoins, FaInfinity, FaTrophy, FaHeartBroken, FaArrowRight } from "react-icons/fa"
import api from "../../api/index"
import BG from "../../components/Background"
import Bar from "../../components/PlayerProps"
import { CartoonButton } from "../../components/assets"
import GameplayPanel from "../../components/GameplayPanel"
import PowerUpTray from "../../components/PowerUpTray"
import useInventory from "../../hooks/useInventory"
import useCountUp from "../../hooks/useCountUp"
import { describeEffect } from "../../assets/powerupMeta"

const GROWTH = 1.25            // meme formule que le serveur (EndlessMode.GROWTH_RATE)
const reward = (stage, bet) => Math.floor(bet * GROWTH ** stage)
const QUICK_BETS = [10, 50, 100, 250]

// Mode Infini: on mise, on a 5 essais par palier. Un palier gagne rapporte mise x 1,25^palier,
// puis on encaisse ou on remise tout au palier suivant. Perdre fait perdre la mise du palier.
export default function Endless() {
    const navigate = useNavigate()
    const [player, setPlayer] = useState(null)
    const [phase, setPhase] = useState("setup")        // setup | playing | cleared | lost
    const [bet, setBet] = useState(50)
    const [stage, setStage] = useState(1)
    const [stake, setStake] = useState(0)              // mise engagee sur le palier en cours
    const [session, setSession] = useState(null)
    const [won, setWon] = useState(0)                  // gain du dernier palier gagne
    const [best, setBest] = useState(0)
    const [error, setError] = useState("")
    const [busy, setBusy] = useState(false)

    // panneau de jeu
    const [localNumber, setLocalNumber] = useState("")
    const [hint, setHint] = useState("")
    const [distance, setDistance] = useState(0)
    const [numbers, setNumbers] = useState([])
    const [shake, setShake] = useState(false)
    const [infos, setInfos] = useState([])
    const [usedPowerups, setUsedPowerups] = useState([])
    const finished = useRef(false)

    const { items: inventory, refresh: refreshInventory } = useInventory(player?.id)

    const loadPlayer = async () => {
        const id = localStorage.getItem("id")
        if (!id) return
        try { setPlayer(await api.get(`/user/${id}`)) } catch (e) { setError(e.message) }
    }
    useEffect(() => { loadPlayer() }, [])
    useEffect(() => { const t = setTimeout(() => setShake(false), 350); return () => clearTimeout(t) }, [shake])

    async function startStage(nextStage, nextBet) {
        setBusy(true); setError("")
        try {
            const s = await api.post("/game/endless/start", { player_id: player.id, bet: nextBet, stage: nextStage })
            setSession(s); setStage(nextStage); setStake(nextBet)
            setLocalNumber(""); setHint(""); setDistance(0); setNumbers([]); setInfos([]); setUsedPowerups([])
            finished.current = false
            setPlayer((p) => ({ ...p, coins: s.coins }))
            setPhase("playing")
            refreshInventory()
        } catch (e) { setError(e.message) } finally { setBusy(false) }
    }

    async function endStage(status) {
        if (finished.current) return 0
        finished.current = true
        try {
            const r = await api.post("/game/endless/end_session", { session_id: session.session_id, player_id: player.id, status, ended: Date.now() / 1000 })
            await loadPlayer()
            return r
        } catch (e) { setError(e.message); return 0 }
    }

    async function applyPowerup(itemId) {
        try {
            const r = await api.post("/game/powerup", { session_id: session.session_id, player_id: player.id, item_id: itemId })
            setUsedPowerups((u) => [...u, itemId])
            setInfos((i) => [...i, { text: describeEffect(r) }])
            if (r.kind === "attempts") setSession((s) => ({ ...s, attempt_left: r.attempt_left, max_attempt: r.max_attempt }))
            refreshInventory()
        } catch (e) { setInfos((i) => [...i, { text: e.message, error: true }]) }
    }

    async function guess() {
        const n = parseInt(localNumber, 10)
        if (!session || finished.current || !Number.isInteger(n)) return
        try {
            const res = await api.post("/game/guess", { session_id: session.session_id, player_id: player.id, number: n })
            setHint(res.result); setDistance(res.distance); setLocalNumber("")
            setSession((s) => ({ ...s, attempt_left: res.attempt_left }))
            if (res.result === "OK") {
                const paid = await endStage("win")
                setWon(paid); setBest(stage)
                setTimeout(() => setPhase("cleared"), 1700)       // le bonbon eclate d'abord
            } else {
                setNumbers((prev) => [...prev, [n, res.result]].slice(-6)); setShake(true)
                if (res.attempt_left <= 0) {
                    await endStage("lose")
                    setTimeout(() => setPhase("lost"), 900)
                }
            }
        } catch (e) { setError(e.message) }
    }

    const coins = player?.coins ?? 0
    const maxBet = coins
    const betOk = Number.isInteger(bet) && bet >= 1 && bet <= maxBet
    const shownWin = useCountUp(phase === "cleared" ? won : 0, 900)

    return (
        <>
            <BG />
            <div className="flex flex-col h-dvh w-full">
                <Bar coins={player?.coins} gems={player?.gems} xp={player?.xp} name={player?.name} level={player?.level} />
                {error && <p role="alert" className="mx-auto mb-2 max-w-3xl rounded-2xl bg-red-500/85 text-white font-bold px-4 py-2 text-center">{error}</p>}

                {phase === "setup" && (
                    <main className="flex-1 min-h-0 overflow-y-auto grid place-items-center p-3">
                        <section className="candy-gloss candy-lip relative w-full max-w-lg rounded-3xl bg-linear-to-b from-[#7a2d99] to-[#3d1560] border-2 border-white/25 p-6 text-center flex flex-col items-center gap-4">
                            <FaInfinity className="text-6xl text-white" aria-hidden="true" />
                            <h1 className="text-4xl text-white">Mode Infini</h1>
                            <p className="text-white/85 font-bold">Trouve le nombre en 5 essais. Chaque palier gagné rapporte ta mise × 1,25 par palier : encaisse, ou remise tout pour monter. Un échec fait perdre la mise du palier.</p>

                            <div className="w-full">
                                <label htmlFor="bet" className="block text-white font-bold mb-1">Ta mise (pièces)</label>
                                <input id="bet" type="number" inputMode="numeric" min={1} max={maxBet} value={bet} onChange={(e) => setBet(parseInt(e.target.value, 10) || 0)}
                                    className="w-full min-h-14 px-4 rounded-xl text-center text-3xl text-white font-black bg-white/15 border-2 border-white/30 focus:outline-none focus:border-yellow-400" />
                                <div className="flex flex-wrap justify-center gap-2 mt-3">
                                    {QUICK_BETS.filter((b) => b <= maxBet).map((b) => (
                                        <button key={b} type="button" onClick={() => setBet(b)} aria-pressed={bet === b}
                                            className={`min-h-11 min-w-14 px-3 rounded-full font-game text-lg ${bet === b ? "bg-yellow-400 text-black" : "bg-white/15 text-white"}`}>{b}</button>
                                    ))}
                                    <button type="button" onClick={() => setBet(maxBet)} className="min-h-11 px-3 rounded-full font-game text-lg bg-white/15 text-white">Tout</button>
                                </div>
                                <p className="mt-3 text-yellow-200 font-bold">Palier 1 : jusqu'à {betOk ? reward(1, bet) : 0} pièces</p>
                                {!betOk && <p className="text-red-200 font-bold">{maxBet < 1 ? "Tu n'as plus de pièces. Gagnes-en en jouant aux autres modes." : `Entre 1 et ${maxBet} pièces.`}</p>}
                            </div>

                            <CartoonButton className="min-h-11 px-8 py-3 text-xl" onClick={() => betOk && !busy && startStage(1, bet)}>
                                {busy ? "Départ…" : "Commencer"}
                            </CartoonButton>
                            <CartoonButton className="min-h-11 px-6 py-2 text-lg" onClick={() => navigate("/")}>Retour</CartoonButton>
                        </section>
                    </main>
                )}

                {phase === "playing" && session && (
                    <>
                        <div className="mx-auto w-full max-w-3xl px-3 pt-1 flex flex-wrap items-center justify-center gap-2 text-sm font-bold">
                            <span className="px-3 py-1 rounded-full bg-yellow-400 text-black">Palier {stage}</span>
                            <span className="px-3 py-1 rounded-full bg-black/40 text-yellow-200 flex items-center gap-1"><FaCoins aria-hidden="true" />Mise {stake}</span>
                            <span className="px-3 py-1 rounded-full bg-black/40 text-white">Gain possible : {reward(stage, stake)}</span>
                            <span className="px-3 py-1 rounded-full bg-black/40 text-white">{session.attempt_left} essai{session.attempt_left > 1 ? "s" : ""} restant{session.attempt_left > 1 ? "s" : ""}</span>
                        </div>
                        <div className="flex flex-1 min-h-0 overflow-y-auto">
                            <GameplayPanel hint={hint} distance={distance} numbers={numbers} isShaking={shake} range={session.max_range}
                                localNumber={localNumber} NumberSetter={setLocalNumber} onGuessr={guess} attempt={numbers.length}
                                showPause={false} gameEnded={hint === "OK"} onGameEnded={() => {}} infos={infos}
                                tray={<PowerUpTray ids={[1, 2, 3, 4, 5, 6]} items={inventory} used={usedPowerups} onUse={applyPowerup} disabled={finished.current} />} />
                        </div>
                    </>
                )}

                {phase === "cleared" && (
                    <main className="flex-1 min-h-0 overflow-y-auto grid place-items-center p-3">
                        <section className="candy-gloss candy-lip relative w-full max-w-md rounded-3xl bg-linear-to-b from-[#1f8a5b] to-[#0d4d34] border-2 border-white/25 p-6 text-center flex flex-col items-center gap-3" role="status">
                            <FaTrophy className="text-6xl text-amber-300" aria-hidden="true" />
                            <h1 className="text-4xl text-white">Palier {stage} réussi !</h1>
                            <div className="flex items-center gap-2 font-game text-4xl text-yellow-300"><FaCoins aria-hidden="true" />+{shownWin}</div>
                            <p className="text-white/85 font-bold">Déjà ajouté à ton solde. Tu peux t'arrêter ici, ou remiser {won} pièces sur le palier {stage + 1} (gain possible : {reward(stage + 1, won)}).</p>
                            {stage >= 100
                                ? <p className="text-yellow-200 font-bold">Palier maximum atteint !</p>
                                : <CartoonButton className="min-h-11 px-6 py-3 text-xl" onClick={() => !busy && startStage(stage + 1, won)}>
                                    <span className="flex items-center justify-center gap-2">{busy ? "Départ…" : <>Continuer <FaArrowRight aria-hidden="true" /></>}</span>
                                  </CartoonButton>}
                            <CartoonButton className="min-h-11 px-6 py-2 text-lg" onClick={() => { setPhase("setup"); setBet(Math.min(50, coins)) }}>Encaisser</CartoonButton>
                        </section>
                    </main>
                )}

                {phase === "lost" && (
                    <main className="flex-1 min-h-0 overflow-y-auto grid place-items-center p-3">
                        <section className="candy-gloss candy-lip relative w-full max-w-md rounded-3xl bg-linear-to-b from-[#8a1f3a] to-[#4d0d1d] border-2 border-white/25 p-6 text-center flex flex-col items-center gap-3" role="status">
                            <FaHeartBroken className="text-6xl text-rose-200" aria-hidden="true" />
                            <h1 className="text-4xl text-white">Perdu au palier {stage}</h1>
                            <p className="text-white/85 font-bold">Le nombre était hors de portée en 5 essais. Tu perds ta mise de {stake} pièces.{best > 0 && ` Meilleur palier réussi cette série : ${best}.`}</p>
                            <CartoonButton className="min-h-11 px-6 py-3 text-xl" onClick={() => { setPhase("setup"); setBest(0); setBet(Math.max(1, Math.min(50, coins))) }}>Rejouer</CartoonButton>
                            <CartoonButton className="min-h-11 px-6 py-2 text-lg" onClick={() => navigate("/")}>Accueil</CartoonButton>
                        </section>
                    </main>
                )}
            </div>
        </>
    )
}
