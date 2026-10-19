import { useThree } from "@react-three/fiber"
import { useEffect } from "react"
import * as THREE from "three"
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js"

// Reflets "studio" pour l'effet bonbon verni, sans fichier HDR externe
export default function Studio() {
    const { gl, scene } = useThree()
    useEffect(() => {
        const pmrem = new THREE.PMREMGenerator(gl)
        const env = pmrem.fromScene(new RoomEnvironment(), 0.04).texture
        scene.environment = env
        return () => { scene.environment = null; env.dispose(); pmrem.dispose() }
    }, [gl, scene])
    return null
}
