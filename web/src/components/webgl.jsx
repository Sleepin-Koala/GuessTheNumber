import { Component } from "react"

// Helpers WebGL sans dependance a three.js (donc dans le bundle principal, tres legers)

export function webglAvailable() {
    try {
        const c = document.createElement("canvas")
        return !!(c.getContext("webgl2") || c.getContext("webgl"))
    } catch { return false }
}

// WebGL "logiciel" (SwiftShader, llvmpipe...) = pas de GPU: la scene 3D saturerait le processeur.
// Dans ce cas on garde le decor leger. `localStorage.force3d = "1"` force la 3D (tests, demos).
export function gpuAccelerated() {
    try {
        if (localStorage.getItem("force3d") === "1") return true
        if (navigator.connection?.saveData) return false
        const gl = document.createElement("canvas").getContext("webgl2") || document.createElement("canvas").getContext("webgl")
        if (!gl) return false
        const info = gl.getExtension("WEBGL_debug_renderer_info")
        const renderer = info ? String(gl.getParameter(info.UNMASKED_RENDERER_WEBGL)) : ""
        return !/swiftshader|llvmpipe|software|softpipe|microsoft basic render/i.test(renderer)
    } catch { return false }
}

// Si le chargement de la scene 3D echoue (hors ligne, WebGL perdu...), on affiche `fallback`
export class Boundary extends Component {
    state = { failed: false }
    static getDerivedStateFromError() { return { failed: true } }
    render() { return this.state.failed ? this.props.fallback : this.props.children }
}
