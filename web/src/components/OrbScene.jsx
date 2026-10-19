import { Canvas, useFrame, useThree } from "@react-three/fiber"
import { useEffect, useMemo, useRef } from "react"
import * as THREE from "three"
import Studio from "./three/Studio"

// Palette: froid (loin) -> citron -> chaud (pres de la reponse)
const GRAPE = new THREE.Color("#8b5cf6")
const ICE = new THREE.Color("#1fa2ff")
const LEMON = new THREE.Color("#ffb300")
const HOT = new THREE.Color("#ff1f5a")
const CONFETTI = ["#ffd23f", "#ff4f7b", "#2ee6a6", "#5ac8fa", "#a78bfa", "#ffffff"]

function heatColor(heat, out) {
    if (heat == null) return out.copy(GRAPE)
    return heat < 0.5
        ? out.copy(ICE).lerp(LEMON, heat * 2)
        : out.copy(LEMON).lerp(HOT, (heat - 0.5) * 2)
}

function useLabelTexture() {
    return useMemo(() => {
        const c = document.createElement("canvas")
        c.width = c.height = 256
        const tex = new THREE.CanvasTexture(c)
        tex.colorSpace = THREE.SRGBColorSpace
        const draw = () => {
            const g = c.getContext("2d")
            g.clearRect(0, 0, 256, 256)
            g.font = '190px "Lilita One", "Arial Black", sans-serif'
            g.textAlign = "center"; g.textBaseline = "middle"
            g.lineJoin = "round"; g.lineWidth = 18; g.strokeStyle = "rgba(20,8,60,.85)"
            g.strokeText("?", 128, 140)
            g.fillStyle = "#fff"; g.fillText("?", 128, 140)
            tex.needsUpdate = true
        }
        draw()
        document.fonts?.load('190px "Lilita One"').then(draw).catch(() => {})
        return tex
    }, [])
}

function useShadowTexture() {
    return useMemo(() => {
        const c = document.createElement("canvas")
        c.width = c.height = 128
        const g = c.getContext("2d")
        const grad = g.createRadialGradient(64, 64, 4, 64, 64, 62)
        grad.addColorStop(0, "rgba(0,0,0,.55)"); grad.addColorStop(1, "rgba(0,0,0,0)")
        g.fillStyle = grad; g.fillRect(0, 0, 128, 128)
        return new THREE.CanvasTexture(c)
    }, [])
}

// Confettis: apparaissent quand la reponse est trouvee
function Burst({ active, reduced }) {
    const mesh = useRef()
    const COUNT = 54
    const data = useMemo(() => Array.from({ length: COUNT }, (_, i) => {
        const a = Math.random() * Math.PI * 2, up = 0.4 + Math.random() * 0.9, sp = 1.6 + Math.random() * 2.4
        return { v: new THREE.Vector3(Math.cos(a) * sp, up * 3.2, Math.sin(a) * sp * 0.6), spin: (Math.random() - 0.5) * 12, size: 0.07 + Math.random() * 0.09, color: new THREE.Color(CONFETTI[i % CONFETTI.length]) }
    }), [])
    const t0 = useRef(null)
    const dummy = useMemo(() => new THREE.Object3D(), [])

    useEffect(() => {
        if (!mesh.current) return
        data.forEach((d, i) => mesh.current.setColorAt(i, d.color))
        mesh.current.instanceColor.needsUpdate = true
    }, [data])

    useEffect(() => { t0.current = active ? performance.now() : null }, [active])

    useFrame(() => {
        if (!mesh.current) return
        const t = t0.current == null ? -1 : (performance.now() - t0.current) / 1000
        data.forEach((d, i) => {
            if (t < 0 || t > 1.8 || reduced) { dummy.scale.setScalar(0); dummy.position.set(0, 0, 0) }
            else {
                dummy.position.set(d.v.x * t, d.v.y * t - 5.2 * t * t, d.v.z * t)
                dummy.rotation.set(t * d.spin, t * d.spin * 0.7, 0)
                dummy.scale.setScalar(d.size * Math.max(0, 1 - t / 1.8) * 2.2)
            }
            dummy.updateMatrix()
            mesh.current.setMatrixAt(i, dummy.matrix)
        })
        mesh.current.instanceMatrix.needsUpdate = true
    })

    return (
        <instancedMesh ref={mesh} args={[undefined, undefined, COUNT]} frustumCulled={false}>
            <octahedronGeometry args={[1, 0]} />
            <meshStandardMaterial roughness={0.35} metalness={0.1} />
        </instancedMesh>
    )
}

function Orb({ heat, hint, shaking, reduced }) {
    const group = useRef(), body = useRef(), mat = useRef(), shadow = useRef()
    const label = useLabelTexture(), shadowTex = useShadowTexture()
    const color = useMemo(() => new THREE.Color(GRAPE), [])
    const target = useMemo(() => new THREE.Color(), [])
    const invalidate = useThree((s) => s.invalidate)
    const S = useRef({ wob: 0, sy: 1, m: 1, popT: 0 })
    const won = hint === "OK"

    useEffect(() => { if (shaking) S.current.wob = 1 }, [shaking])
    useEffect(() => { S.current.popT = 0 }, [won])
    useEffect(() => { invalidate() }, [heat, hint, shaking, invalidate])

    useFrame((state, dt) => {
        const s = S.current, t = state.clock.elapsedTime
        const k = (rate) => (reduced ? 1 : 1 - Math.exp(-dt * rate))

        // temperature de la reponse -> couleur
        heatColor(heat, target)
        color.lerp(target, k(6))
        mat.current.color.copy(color)
        mat.current.emissive.copy(color).multiplyScalar(0.1)

        // trop petit = le bonbon gonfle, trop grand = il s'ecrase
        const ty = hint === "MOINS" ? 1.1 : hint === "PLUS" ? 0.9 : 1
        s.sy += (ty - s.sy) * k(10)
        const sxz = 1 + (1 - s.sy) * 0.8

        // rebond d'echec
        s.wob *= reduced ? 0 : Math.exp(-dt * 4.5)

        // pop a la victoire: petit gonflement puis disparition
        if (won) s.popT += dt
        const pm = won ? (s.popT < 0.14 ? 1 + (s.popT / 0.14) * 0.22 : Math.max(0, 1.22 * (1 - (s.popT - 0.14) / 0.16))) : 1
        s.m += (pm - s.m) * Math.min(1, dt * 30)

        const g = group.current
        g.position.y = reduced ? 0 : Math.sin(t * 1.6) * 0.07
        g.rotation.y = reduced ? 0 : Math.sin(t * 0.5) * 0.25
        g.rotation.z = Math.sin(t * 38) * 0.2 * s.wob
        g.scale.set(sxz * s.m, s.sy * s.m, sxz * s.m)
        shadow.current.scale.setScalar((1.9 - g.position.y * 2) * (0.4 + 0.6 * Math.min(1, s.m)))
    })

    return (
        <>
            <mesh ref={shadow} position={[0, -1.4, 0]} rotation={[-Math.PI / 2, 0, 0]}>
                <planeGeometry args={[1.6, 1.6]} />
                <meshBasicMaterial map={shadowTex} transparent depthWrite={false} />
            </mesh>
            <group ref={group}>
                <mesh ref={body}>
                    <sphereGeometry args={[1, 64, 64]} />
                    <meshPhysicalMaterial ref={mat} roughness={0.16} metalness={0} clearcoat={1} clearcoatRoughness={0.06} envMapIntensity={0.55} />
                </mesh>
                <mesh position={[0, 0, 1.03]}>
                    <planeGeometry args={[1.25, 1.25]} />
                    <meshBasicMaterial map={label} transparent depthWrite={false} opacity={won ? 0 : 1} />
                </mesh>
            </group>
            <Burst active={won} reduced={reduced} />
        </>
    )
}

export default function OrbScene({ heat, hint, shaking, reduced }) {
    return (
        <Canvas dpr={[1, 1.75]} camera={{ position: [0, 0.1, 4.6], fov: 38 }}
            frameloop={reduced ? "demand" : "always"} gl={{ antialias: true, alpha: true }}
            style={{ touchAction: "pan-y" }}>
            <Studio />
            <ambientLight intensity={0.22} />
            <directionalLight position={[3, 4, 5]} intensity={1.3} />
            <pointLight position={[-3, -1, 2]} intensity={14} color="#8b6cff" />
            <Orb heat={heat} hint={hint} shaking={shaking} reduced={reduced} />
        </Canvas>
    )
}
