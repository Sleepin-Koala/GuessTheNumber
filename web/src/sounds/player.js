// Sons du jeu. Howler (la bibliotheque audio) n'est charge qu'au premier son joue, et chaque fichier n'est
// decode qu'a sa premiere utilisation: rien de tout cela ne ralentit l'affichage de la page d'accueil.
// Les fichiers sont importes (et donc inclus dans le build avec un nom hache), contrairement aux anciens
// chemins "src/sounds/..." qui n'existaient qu'avec le serveur de developpement.
import click from "./click.wav"
import notAllowed from "./not_allowed.mp3"
import wrong from "./not.mp3"
import win from "./win.wav"
import buy from "./buy.mp3"
import fail from "./fail.mp3"
import main from "./main.mp3"

export const SOUNDS = { click, notAllowed, wrong, win, buy, fail, main }

const cache = {}
let howlerLoading

// Reglage "Effets sonores" (Parametres): actif tant qu'il n'a pas ete explicitement coupe
export const soundEnabled = () => {
    try { return localStorage.getItem("sound") !== "false" } catch { return true }
}

async function howl(src, options = {}) {
    howlerLoading ??= import("howler")
    const { Howl } = await howlerLoading
    return (cache[src] ??= new Howl({ src: [src], volume: 1, ...options }))
}

export function play(src) {
    if (!soundEnabled()) return
    howl(src).then((h) => h.play()).catch(() => { /* audio indisponible: le jeu continue sans son */ })
}

export const music = {
    play() { if (soundEnabled()) howl(SOUNDS.main, { loop: true }).then((h) => h.play()).catch(() => {}) },
    stop() { cache[SOUNDS.main]?.stop() },
}
