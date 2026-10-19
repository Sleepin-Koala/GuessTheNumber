import api, { quietly } from "./index"

// Le "compte" = un identifiant public (id) + un jeton secret (token), tous deux gardes dans localStorage.
// Le jeton n'est donne qu'a la creation du compte: sans lui (ou sans le code de recuperation) le compte est perdu.
export const getToken = () => localStorage.getItem("token")

export function saveAccount({ id, token }) {
    localStorage.setItem("id", id)
    if (token) localStorage.setItem("token", token)
}

export async function createAccount() {
    const player = await api.post("/user/new_player")
    saveAccount(player)
    return player
}

/**
 * Retourne le joueur courant, en creant ou en migrant le compte au besoin:
 *  - jeton present      -> on verifie qu'il est toujours reconnu (sinon `null` + evenement "gtn:auth-lost",
 *                          jamais de nouveau compte en silence: on perdrait la progression);
 *  - ancien compte (id sans jeton, cree avant l'authentification) -> on reclame un jeton, une seule fois;
 *  - rien du tout       -> nouveau compte.
 */
export async function ensureAccount() {
    if (getToken()) {
        try { return await api.get("/user/me") } catch (e) { if (e.status === 401) return null; throw e }
    }
    const legacyId = localStorage.getItem("id")
    if (legacyId) {
        try {
            const player = await api.post("/user/claim", { player_id: legacyId })
            saveAccount(player)
            return player
        } catch (e) { if (e.status !== 409) throw e }      // 409: deja reclame par quelqu'un d'autre ou inconnu
    }
    return createAccount()
}

// Restaure un compte a partir d'un code de recuperation (= le jeton). Rien n'est modifie si le code est refuse.
export async function restoreWithToken(code) {
    const previous = getToken()
    localStorage.setItem("token", code.trim())
    try {
        const player = await quietly(() => api.get("/user/me"))
        saveAccount({ id: player.id, token: code.trim() })
        return player
    } catch (e) {
        if (previous) localStorage.setItem("token", previous); else localStorage.removeItem("token")
        throw e
    }
}

// Lance la verification / creation du compte UNE fois et sans bloquer l'affichage. Les ecrans qui ont besoin du
// compte (tous sauf l'accueil, qui l'attend lui-meme) passent par <AccountGate> en attendant ce resultat.
let account
export function startAccount() {
    account ??= ensureAccount().catch((e) => { console.warn("Account check failed", e); return null })
    return account
}
