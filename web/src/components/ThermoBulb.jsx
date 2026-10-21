import { useLayoutEffect, useRef } from "react"
import { gsap } from "gsap"

// Bulbe du thermometre: flocon qui flotte quand la zone est large (froid), flamme vivante quand elle se resserre (chaud).
const FLAKE = "M24 3v42M24 3l-5 6M24 3l5 6M24 45l-5-6M24 45l5-6M3.8 15.5l40.4 17M3.8 15.5l7.4-.6M3.8 15.5l3.2 6.9M44.2 32.5l-7.4.6M44.2 32.5l-3.2-6.9M3.8 32.5l40.4-17M3.8 32.5l7.4.6M3.8 32.5l3.2-6.9M44.2 15.5l-7.4-.6M44.2 15.5l-3.2 6.9"

export default function ThermoBulb({ kind, warmth, color }) {
    const root = useRef(null)

    useLayoutEffect(() => {
        if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return
        const ctx = gsap.context(() => {
            if (kind === "ice") {
                gsap.to(".flake", { rotation: 360, duration: 16, ease: "none", repeat: -1, transformOrigin: "50% 50%" })
                gsap.to(".flake-wrap", { y: -3, scale: 1.06, duration: 2.2, ease: "sine.inOut", yoyo: true, repeat: -1 })
                gsap.utils.toArray(".snow").forEach((el, i) => {
                    gsap.fromTo(el, { y: -12, x: "random(-16,16)", opacity: 0 },
                        { y: 30, x: "+=random(-10,10)", opacity: 1, duration: "random(2.2,3.6)", delay: i * 0.45, ease: "sine.inOut", repeat: -1, repeatRefresh: true,
                          keyframes: { opacity: [0, 1, 1, 0] } })
                })
            } else {
                // trois couches de flamme qui vacillent a des rythmes differents
                gsap.utils.toArray(".fl").forEach((el, i) => {
                    gsap.set(el, { transformOrigin: "50% 100%" })
                    gsap.to(el, { scaleY: "random(1.06,1.22)", scaleX: "random(0.86,0.97)", skewX: "random(-8,8)", duration: `random(${0.16 + i * 0.05},${0.34 + i * 0.07})`,
                        ease: "sine.inOut", yoyo: true, repeat: -1, repeatRefresh: true })
                })
                gsap.utils.toArray(".ember").forEach((el, i) => {
                    gsap.fromTo(el, { y: 4, x: "random(-7,7)", opacity: 1, scale: 1 },
                        { y: -34, x: "+=random(-8,8)", opacity: 0, scale: 0.3, duration: "random(0.9,1.5)", delay: i * 0.28, ease: "power1.out", repeat: -1, repeatRefresh: true })
                })
            }
        }, root)
        return () => ctx.revert()
    }, [kind])

    const k = Math.min(1, 0.55 + warmth * 0.65)       // la flamme grandit avec la temperature

    return (
        <span ref={root} aria-hidden="true" className="relative z-10 -mr-3 grid h-11 w-11 [@media(max-height:900px)]:h-9 [@media(max-height:900px)]:w-9 shrink-0 place-items-center rounded-full ring-2 ring-white/30 transition-[box-shadow,background] duration-500"
            style={{ background: kind === "ice" ? "radial-gradient(circle at 35% 28%, #fff9 0, transparent 38%), #1b4f9c" : "radial-gradient(circle at 35% 28%, #fff6 0, transparent 38%), #4a1208",
                     boxShadow: `0 0 ${10 + warmth * 24}px ${color}, inset 0 -4px 0 rgba(0,0,0,.25)` }}>
            {kind === "ice" ? (
                <>
                    {[0, 1, 2, 3, 4].map((i) => <span key={i} className="snow absolute left-1/2 top-1/2 h-1 w-1 rounded-full bg-white/90" />)}
                    <span className="flake-wrap grid place-items-center">
                        <svg className="flake" width="36" height="36" viewBox="0 0 48 48" fill="none" stroke="#e6f6ff" strokeWidth="3.2" strokeLinecap="round" style={{ filter: "drop-shadow(0 0 5px #7fd4ff)" }}><path d={FLAKE} /></svg>
                    </span>
                </>
            ) : (
                <>
                    {[0, 1, 2, 3].map((i) => <span key={i} className="ember absolute bottom-3 left-1/2 h-1 w-1 rounded-full bg-amber-300" style={{ boxShadow: "0 0 6px #ffb347" }} />)}
                    <svg width="40" height="56" viewBox="0 0 40 56" className="absolute bottom-1 overflow-visible" style={{ transform: `scale(${k})`, transformOrigin: "50% 100%", filter: `drop-shadow(0 0 ${6 + warmth * 10}px #ff7a1a)` }}>
                        <path className="fl" d="M20 1C25 14 37 21 35 37C34 49 27 55 20 55C13 55 6 49 5 37C3 22 15 15 20 1Z" fill="#ff4a12" />
                        <path className="fl" d="M20 12C24 21 31 26 30 37C29 46 25 51 20 51C15 51 11 46 10 37C9 27 17 22 20 12Z" fill="#ff9a1f" />
                        <path className="fl" d="M20 26C22.5 31 26 34 25 40C24.5 45 22.5 48 20 48C17.5 48 15.5 45 15 40C14 34 17.5 31 20 26Z" fill="#ffe27a" />
                    </svg>
                </>
            )}
        </span>
    )
}
