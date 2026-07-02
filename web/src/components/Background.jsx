
import "../assets/styles/anim.css"

export default function Bg() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      <svg
        viewBox="0 0 1200 800"
        preserveAspectRatio="xMidYMid slice"
        className="w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Dégradé principal : nuit urbaine */}
          <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#0a0f2c" />
            <stop offset="40%" stopColor="#1a0f3c" />
            <stop offset="100%" stopColor="#2d1b4e" />
          </linearGradient>

          {/* Dégradé pour les rails */}
          <linearGradient id="railGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#ff3366" />
            <stop offset="100%" stopColor="#ff9933" />
          </linearGradient>

          {/* Pattern de grille (tags) */}
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#ffffff10" strokeWidth="1" />
          </pattern>

          {/* Filtre de glow néon */}
          <filter id="neonGlow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Fond */}
        <rect width="1200" height="800" fill="url(#bgGrad)" />
        <rect width="1200" height="800" fill="url(#grid)" />

        {/* Lignes de perspective (rails) */}
        <g stroke="url(#railGrad)" strokeWidth="4" opacity="0.6">
          <line x1="0" y1="750" x2="600" y2="400" />
          <line x1="1200" y1="750" x2="600" y2="400" />
          <line x1="200" y1="750" x2="600" y2="400" />
          <line x1="1000" y1="750" x2="600" y2="400" />
        </g>

        {/* Tags graffiti (flèches, étoiles, éclairs) */}
        <g fill="none" stroke="#ffcc00" strokeWidth="3" opacity="0.5" filter="url(#neonGlow)">
          <path d="M 100 200 L 140 160 L 180 200" />
          <path d="M 140 160 L 140 220" />
          <path d="M 950 250 L 990 210 L 1030 250" />
          <path d="M 990 210 L 990 270" />
          <polygon points="800,150 820,190 860,190 830,215 845,255 800,230 755,255 770,215 740,190 780,190" />
        </g>

        {/* Éclairs / zigzag */}
        <g fill="#ff3366" opacity="0.4" filter="url(#neonGlow)">
          <polyline points="1050,400 1080,450 1040,480 1070,530" stroke="#ff3366" strokeWidth="4" fill="none" />
          <polyline points="150,500 180,550 140,580 170,630" stroke="#ff9933" strokeWidth="4" fill="none" />
        </g>

        {/* Nombres stylisés (street art) – avec police "Bangers" ou "Poppins" via className */}
        {[
          { x: 200, y: 300, text: "?",  size: 120, rot: -10, color: "#ffcc00", delay: "0s", anim: "shake1" },
          { x: 900, y: 350, text: "42", size: 90,  rot: 15,  color: "#ff66cc", delay: "0.4s", anim: "shake2" },
          { x: 500, y: 200, text: "100",size: 100, rot: 5,   color: "#66ffcc", delay: "0.8s", anim: "shake3" },
          { x: 750, y: 550, text: "1",  size: 110, rot: -8,  color: "#ff9933", delay: "1.2s", anim: "shake1" },
          { x: 100, y: 580, text: "50", size: 80,  rot: 12,  color: "#33ccff", delay: "1.6s", anim: "shake2" },
          { x: 900  , y: 180, text:"99", size: 85,  rot: -15, color: "#ff3366", delay: "2s",   anim: "shake3" },
        ].map(({ x, y, text, size, rot, color, delay, anim }, i) => (
          <text
            key={i}
            x={x}
            y={y}
            fontFamily="'Bangers', 'Poppins', system-ui"
            fontSize={size}
            fontWeight="900"
            fill={color}
            stroke="#1a0f3c"
            strokeWidth="6"
            paintOrder="stroke"
            transform={`rotate(${rot} ${x} ${y})`}
            style={{ animation: `${anim} 2.5s ease-in-out infinite ${delay}` }}
          >
            {text}
          </text>
        ))}

        {/* Graffiti "GAME" stylisé en bas */}
        <text
          x="600" y="750"
          fontFamily="'Bangers', system-ui"
          fontSize="70"
          fontWeight="900"
          fill="none"
          stroke="#ffcc00"
          strokeWidth="4"
          textAnchor="middle"
          opacity="0.3"
          style={{ animation: "pulse 2s infinite" }}
        >
          GUESS THE NUMBER
        </text>

        {/* Quartiers d'orange / magenta / cyan (effet néon) */}
        <circle cx="300" cy="650" r="8" fill="#ff3366" filter="url(#neonGlow)" style={{ animation: "float1 1.5s infinite alternate" }} />
        <circle cx="850" cy="700" r="12" fill="#33ffcc" filter="url(#neonGlow)" style={{ animation: "float2 1.8s infinite alternate" }} />
        <circle cx="100" cy="150" r="6" fill="#ffcc00" filter="url(#neonGlow)" style={{ animation: "float3 1.2s infinite alternate" }} />
        <circle cx="1100" cy="650" r="10" fill="#ff66cc" filter="url(#neonGlow)" style={{ animation: "float1 2s infinite alternate" }} />

        {/* Lignes de vitesse (background dynamique) */}
        <g stroke="#ffffff30" strokeWidth="2" opacity="0.5">
          {[...Array(20)].map((_, i) => (
            <line
              key={i}
              x1={Math.random() * 1200}
              y1={Math.random() * 800}
              x2={Math.random() * 1200}
              y2={Math.random() * 800}
              style={{ animation: `dashLine ${2 + i * 0.1}s linear infinite` }}
            />
          ))}
        </g>
      </svg>
    </div>
  );
}