import { POWERUPS } from "../assets/powerupMeta"

/**
 * Boutons des power-ups que le joueur possede (et n'a pas encore utilises dans cette partie).
 * Ne rend rien si l'inventaire est vide.
 */
export default function PowerUpTray({ ids, items, used, onUse, disabled }) {
    const shown = ids.filter((id) => (items[id] ?? 0) > 0 && !used.includes(id))
    if (shown.length === 0) return null

    return (
        <div className="flex flex-wrap items-center justify-center gap-2" role="group" aria-label="Power-ups">
            {shown.map((id) => (
                <button key={id} type="button" disabled={disabled} onClick={() => onUse(id)}
                    aria-label={`${POWERUPS[id].name}, ${items[id]} en stock`} title={POWERUPS[id].name}
                    className="relative grid place-items-center w-11 h-11 rounded-full text-xl text-amber-950 bg-linear-to-b from-yellow-300 to-orange-400 shadow-[0_3px_0_#b45309] active:translate-y-0.5 active:shadow-[0_1px_0_#b45309] disabled:opacity-40 transition-transform">
                    {POWERUPS[id].icon}
                    <span className="absolute -top-1 -right-1 grid place-items-center min-w-5 h-5 px-1 rounded-full bg-black text-white text-xs font-bold">{items[id]}</span>
                </button>
            ))}
        </div>
    )
}
