import { SOUNDS, play, music } from "../sounds/player"

// Meme interface qu'avant, mais sans etat React: les fonctions sont stables et le chargement audio est differe.
const api = {
    inGameSound: {
        click: () => play(SOUNDS.click),
        notallowedclick: () => play(SOUNDS.notAllowed),
        isFalse: () => play(SOUNDS.wrong),
        onLose: () => play(SOUNDS.fail),
        onWin: () => play(SOUNDS.win),
    },
    mainMusic: music,
    situationSound: { onBuy: () => play(SOUNDS.buy) },
}

export default function useGameSound() {
    return api
}
