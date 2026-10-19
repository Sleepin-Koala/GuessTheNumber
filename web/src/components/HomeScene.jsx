import { Canvas, useFrame, useThree } from "@react-three/fiber"
import { useEffect, useMemo, useRef } from "react"
import * as THREE from "three"
import Studio from "./three/Studio"
import useMediaQuery from "../hooks/useMediaQuery"

const NIGHT = "#150b30"
const COLORS = ["#ff4f7b", "#ffd23f", "#2ee6a6", "#4cb8ff", "#9b6bff", "#ff9f1c"]

// Autocollant "chiffre" pose sur chaque bonbon (une texture par chiffre, partagee)
function useDigitTextures() {
    return useMemo(() => {
        const make = (d) => {
            const c = document.createElement("canvas")
            c.width = c.height = 128
            const tex = new THREE.CanvasTexture(c)
            tex.colorSpace = THREE.SRGBColorSpace
            const draw = () => {
                const g = c.getContext("2d")
                g.clearRect(0, 0, 128, 128)
                g.font = '96px "Lilita One", "Arial Black", sans-serif'
                g.textAlign = "center"; g.textBaseline = "middle"
                g.lineJoin = "round"; g.lineWidth = 12; g.strokeStyle = "rgba(25,10,70,.8)"
                g.strokeText(String(d), 64, 72); g.fillStyle = "#fff"; g.fillText(String(d), 64, 72)
                tex.needsUpdate = true
            }
            draw()
            return { tex, draw }
        }
        const list = Array.from({ length: 10 }, (_, d) => make(d))
        document.fonts?.load('96px "Lilita One"').then(() => list.forEach((t) => t.draw())).catch(() => {})
        return list.map((t) => t.tex)
    }, [])
}

function Candies({ count, reduced, spread }) {
    const refs = useRef([])
    const textures = useDigitTextures()
    const items = useMemo(() => Array.from({ length: count }, (_, i) => ({
        x: (Math.random() - 0.5) * 24 * spread, y: (Math.random() - 0.5) * 17, z: -3 - Math.random() * 9,
        s: 0.45 + Math.random() * 0.55, speed: 0.15 + Math.random() * 0.3, phase: Math.random() * 6.28,
        color: COLORS[i % COLORS.length], digit: Math.floor(Math.random() * 10), turn: (Math.random() - 0.5) * 0.5,
    })), [count, spread])

    useFrame((state, dt) => {
        const t = state.clock.elapsedTime
        items.forEach((it, i) => {
            const g = refs.current[i]
            if (!g) return
            if (!reduced) { it.y += it.speed * dt; if (it.y > 9) it.y = -9 }
            g.position.set(it.x + (reduced ? 0 : Math.sin(t * 0.5 + it.phase) * 0.35), it.y, it.z)
            g.rotation.set(0, reduced ? 0 : Math.sin(t * 0.4 + it.phase) * 0.5, reduced ? 0 : it.turn * Math.sin(t * 0.6 + it.phase))
        })
    })

    return items.map((it, i) => (
        <group key={i} ref={(el) => (refs.current[i] = el)} scale={it.s}>
            <mesh>
                <sphereGeometry args={[1, 40, 40]} />
                <meshPhysicalMaterial color={it.color} roughness={0.2} clearcoat={1} clearcoatRoughness={0.08} envMapIntensity={0.9} emissive={it.color} emissiveIntensity={0.18} />
            </mesh>
            <mesh position={[0, 0, 1.02]}>
                <planeGeometry args={[1.15, 1.15]} />
                <meshBasicMaterial map={textures[it.digit]} transparent depthWrite={false} fog={false} />
            </mesh>
        </group>
    ))
}

function Stars({ reduced }) {
    const ref = useRef()
    const positions = useMemo(() => {
        const a = new Float32Array(240 * 3)
        for (let i = 0; i < 240; i++) { a[i * 3] = (Math.random() - 0.5) * 40; a[i * 3 + 1] = (Math.random() - 0.5) * 24; a[i * 3 + 2] = -14 - Math.random() * 6 }
        return a
    }, [])
    useFrame((_, dt) => { if (!reduced && ref.current) ref.current.rotation.z += dt * 0.004 })
    return (
        <points ref={ref}>
            <bufferGeometry><bufferAttribute attach="attributes-position" args={[positions, 3]} /></bufferGeometry>
            <pointsMaterial size={0.07} color="#ffffff" transparent opacity={0.7} sizeAttenuation fog={false} />
        </points>
    )
}

// leger effet de profondeur: la camera suit doucement le pointeur
function Rig({ reduced }) {
    const pointer = useRef({ x: 0, y: 0 })
    const camera = useThree((s) => s.camera)
    useEffect(() => {
        if (reduced) return
        const move = (e) => { pointer.current.x = (e.clientX / window.innerWidth - 0.5) * 2; pointer.current.y = (e.clientY / window.innerHeight - 0.5) * 2 }
        window.addEventListener("pointermove", move)
        return () => window.removeEventListener("pointermove", move)
    }, [reduced])
    useFrame((_, dt) => {
        const k = 1 - Math.exp(-dt * 2)
        camera.position.x += (pointer.current.x * 0.7 - camera.position.x) * k
        camera.position.y += (-pointer.current.y * 0.45 - camera.position.y) * k
        camera.lookAt(0, 0, -4)
    })
    return null
}

export default function HomeScene({ reduced }) {
    const wide = useMediaQuery("(min-width: 768px)")
    return (
        <Canvas dpr={[1, 1.5]} camera={{ position: [0, 0, 4], fov: 55 }} frameloop={reduced ? "demand" : "always"}
            gl={{ antialias: true, alpha: true }}>
            <fog attach="fog" args={[NIGHT, 9, 26]} />
            <Studio />
            <ambientLight intensity={0.5} />
            <directionalLight position={[3, 5, 4]} intensity={2} />
            <pointLight position={[-5, -2, 0]} intensity={30} color="#7c4dff" />
            <pointLight position={[5, 3, -2]} intensity={22} color="#ff4f7b" />
            <Stars reduced={reduced} />
            <Candies count={wide ? 30 : 16} reduced={reduced} spread={wide ? 1 : 0.5} />
            <Rig reduced={reduced} />
        </Canvas>
    )
}
