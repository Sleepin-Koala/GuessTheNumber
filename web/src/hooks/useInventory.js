import { useCallback, useEffect, useState } from "react"
import api from "../api/index"

// Inventaire du joueur: { "3": 2, "5": 1 } (id d'objet -> quantite)
export default function useInventory(playerId) {
    const [items, setItems] = useState({})

    const refresh = useCallback(async () => {
        if (!playerId) return
        try {
            const res = await api.get(`/shop/inventory/${playerId}`)
            setItems(res.items ?? {})
        } catch (e) {
            console.error(e)
        }
    }, [playerId])

    useEffect(() => { refresh() }, [refresh])

    return { items, refresh }
}
